from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timezone import now, make_aware, is_aware
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta, datetime, time, timezone
import json
import random
from .models import ImpactRecord, Task, UserTask
from django.utils import timezone
from django.db.models import Sum



@login_required
def home(request):
    return render(request, 'climateapp/home.html')


@login_required
def calculator(request):
    return render(request, 'climateapp/calculator.html')


@login_required
def impact_history(request):
    history = ImpactRecord.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'climateapp/history.html', {'history': history})


@csrf_exempt
@login_required
def mark_task_complete(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            task_states = data.get('task_states', [])
            if not task_states:
                return JsonResponse({'status': 'error', 'message': 'No task states provided'}, status=400)

            for item in task_states:
                task_id = item.get('id')
                completed = item.get('completed', False)

                task = Task.objects.get(id=task_id)
                user_task, _ = UserTask.objects.get_or_create(
                    user=request.user, 
                    task=task, 
                    assigned_at=now().date()
                )

                user_task.completed = completed
                user_task.completed_at = now() if completed else None
                user_task.save()

            return JsonResponse({'status': 'success'})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def save_impact_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        today = now().date()

        ImpactRecord.objects.filter(user=request.user, created_at__date=today).delete()

        record = ImpactRecord.objects.create(
            user=request.user,
            diet_co2=data.get('diet', 0),
            commute_co2=data.get('commute', 0),
            energy_co2=data.get('energy', 0),
            water_co2=data.get('water', 0),
            total_co2=data.get('total', 0)
        )

        return JsonResponse({'status': 'created', 'record_id': record.id})

    return JsonResponse({'status': 'error'}, status=400)


def about(request):
    return render(request, 'climateapp/about.html')


def result(request):
    return render(request, 'climateapp/result.html')


@login_required
def tips(request):
    today = now().date()
    weekday = today.weekday()

    # Auto-refresh tasks for today
    existing_today = UserTask.objects.filter(user=request.user, assigned_at=today)
    if not existing_today.exists():
        UserTask.objects.filter(user=request.user).delete()
        random_tasks = Task.objects.order_by('?')[:3]
        for task in random_tasks:
            UserTask.objects.create(user=request.user, task=task, assigned_at=today)

    user_tasks = UserTask.objects.filter(user=request.user, assigned_at=today)
    tasks = [{
        'id': ut.task.id,
        'title': ut.task.title,
        'description': ut.task.description,
        'completed': ut.completed
    } for ut in user_tasks]

    record = ImpactRecord.objects.filter(user=request.user, created_at__date=today).first()

    tips = []
    if record:
    # Diet tips
     if record.diet_co2 > 120:
        tips.append("🥩 Reduce meat or dairy meals—plant-based diets are lower CO₂.")
        tips.append("🌿 Try a plant-based recipe this week to cut carbon footprint.")
     elif record.diet_co2 > 80:
        tips.append("🥗 Add more vegetarian meals to reduce your carbon diet impact.")
        tips.append("🍳 Choose local, seasonal foods when possible.")

    # Commute tips
     if record.commute_co2 > 160:
        tips.append("🚗 Try carpooling or public transport instead of solo driving.")
        tips.append("🛴 Consider biking or using an e-scooter for short trips.")
     elif record.commute_co2 > 100:
        tips.append("🚌 Use public transport for some of your trips this week.")
        tips.append("🚶 Walk to nearby destinations instead of using a vehicle.")

    # Energy tips
     if record.energy_co2 > 10:
        tips.append("💡 Switch to LED bulbs and reduce AC use where possible.")
        tips.append("🖥️ Enable power-saving mode on all electronics.")
     elif record.energy_co2 > 5:
        tips.append("🔌 Turn off devices instead of leaving them on standby.")
        tips.append("🌬️ Use fans before switching on the AC.")

    # Water tips
     if record.water_co2 > 5:
        tips.append("🚿 Shorten showers and avoid wasteful taps.")
        tips.append("🛁 Skip the bath and take quick showers instead.")
     elif record.water_co2 > 3:
        tips.append("💧 Use a bucket for washing and water plants in the evening.")
        tips.append("🌱 Reuse RO or leftover water for plants.")
    else:
     tips = [
        "🚲 Bike or walk short distances.",
        "🔌 Unplug devices not in use to save energy."
      ]


    weekly_themes = [
        "♻️ Zero-Waste Week: Ditch all disposables!",
        "🌞 Solar Week: Learn about renewable energy.",
        "🌱 Plant-Based Week: Eat vegan 3 times this week.",
        "🚪 Car-Free Week: Ditch your car for a couple days.",
        "💧 Water Saver Week: Reduce water use by 20%.",
        "🔌 Smart Energy Week: Use power-saving devices.",
        "🧹 Cleanup Week: Participate in local cleanups!"
    ]
    weekly_theme = weekly_themes[weekday]

    daily_challenges = [
        "🌿 Go meatless today!",
        "🚿 Limit your shower to 5 minutes.",
        "🚲 Walk or bike today.",
        "🔌 Unplug unused devices.",
        "♻️ Repurpose instead of throwing out.",
        "💡 Replace a bulb with an LED.",
        "🧺 Only wash full laundry loads."
    ]
    daily_challenge = daily_challenges[weekday]

    trivia_list = [
        "🧠 1 kg of beef emits up to 60 kg CO₂.",
        "🧠 Turning off devices saves ~10% energy.",
        "🧠 A 10-min shower uses up to 100L of water.",
        "🧠 LEDs use 90% less power than normal bulbs.",
        "🧠 Biking just 1x/week helps cut urban CO₂."
    ]
    trivia = random.choice(trivia_list)

    community_tips = [
        "🧱 Start a community compost bin!",
        "🧱 Host a local clothes swap.",
        "🧱 Plant a tree with neighbors.",
        "🧱 Share public transport to events."
    ]
    community_tip = random.choice(community_tips)

    app_suggestions = [
        "📱 JouleBug: Track your daily sustainability wins!",
        "📱 Oroeco: Visualize your carbon impact.",
        "📱 TooGoodToGo: Save food from waste nearby.",
        "📱 HappyCow: Find vegan/eco-friendly restaurants."
    ]
    app_tip = random.choice(app_suggestions)

    return render(request, 'climateapp/tips.html', {
        'tips': tips,
        'weekly_theme': weekly_theme,
        'daily_challenge': daily_challenge,
        'trivia': trivia,
        'community_tip': community_tip,
        'app_tip': app_tip,
        'tasks': tasks,
        'has_data': bool(record),
    })


def get_weekly_progress(user):
    today = now().date()
    week_start = today - timedelta(days=today.weekday())
    records = ImpactRecord.objects.filter(user=user, created_at__date__gte=week_start)

    return {
        'diet': sum(r.diet_co2 for r in records),
        'commute': sum(r.commute_co2 for r in records),
        'energy': sum(r.energy_co2 for r in records),
        'water': sum(r.water_co2 for r in records),
        'total': sum(r.total_co2 for r in records),
        'days': records.count()
    }

def profile(request):
    user = request.user
    today = now().date()

    # All assigned tasks for today
    user_tasks = UserTask.objects.filter(user=user, assigned_at=today)
    total_tasks = user_tasks.count()
    completed_tasks = user_tasks.filter(completed=True).count()

    # Tree growth percentage logic
    if total_tasks > 0:
        tree_growth = int((completed_tasks / total_tasks) * 100)
    else:
        tree_growth = 0

    # Tree stage based on growth percent

    if tree_growth >= 75:
        tree_stage = 3
    elif tree_growth >= 50:
        tree_stage = 2
    elif tree_growth >= 25:
        tree_stage = 1
    else:
        tree_stage = 0

    # Animate growth if recently completed a task
    animate_growth = False
    latest = user_tasks.filter(completed=True).order_by('-completed_at').first()
    if latest and latest.completed_at:
        time_diff = now() - latest.completed_at
        if time_diff.total_seconds() < 10:
            animate_growth = True

    # Weekly progress bar (sum of emissions)
    this_week = now().date().isocalendar().week
    week_records = ImpactRecord.objects.filter(user=user, created_at__week=this_week)

    progress = week_records.aggregate(
        diet=Sum('diet_co2') or 0,
        commute=Sum('commute_co2') or 0,
        energy=Sum('energy_co2') or 0,
        water=Sum('water_co2') or 0
    )

    return render(request, 'climateapp/profile.html', {
        'tree_growth': tree_growth,
        'tree_stage': tree_stage,
        'animate_growth': animate_growth,
        'progress': progress,
    })
