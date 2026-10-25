from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import UserProfile, InsuranceAgent, InsuranceHistory
import pandas as pd
import joblib

model = joblib.load('recommender/insurance_model.pkl')
le_dict = joblib.load('recommender/label_encoders.pkl')

def calculate_risk(age, smoking, fitness, late_night, accidents):
    score = 15
    if age > 50: score += 15
    if smoking == 'Yes': score += 20
    elif smoking == 'Sometimes': score += 10
    if fitness == 'Poor': score += 20
    if late_night == 'Yes': score += 10
    elif late_night == 'Sometimes': score += 5
    score += (accidents * 10)
    return min(score, 100)

def register_page(request):
    if request.method == 'POST':
        user_name = request.POST['username']
        pass_word = request.POST['password']
        if not User.objects.filter(username=user_name).exists():
            new_user = User.objects.create_user(username=user_name, password=pass_word)
            UserProfile.objects.create(user=new_user)
            login(request, new_user)
            return redirect('home')
        else:
            return render(request, 'register.html', {'error': 'Username already taken!'})
    return render(request, 'register.html')

def login_page(request):
    if request.method == 'POST':
        user_name = request.POST['username']
        pass_word = request.POST['password']
        user = authenticate(request, username=user_name, password=pass_word)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid Username or Password!'})
    return render(request, 'login.html')

def logout_user(request):
    logout(request)
    return redirect('login_page')

@login_required(login_url='login_page')
def home(request):
    if request.method == 'POST':
        age = int(request.POST['age'])
        income = int(request.POST['income'])
        dependents = int(request.POST['dependents'])
        driving_km = int(request.POST['driving_km'])
        accidents = int(request.POST['accidents'])
        smoking = request.POST['smoking']
        fitness = request.POST['fitness']
        late_night = request.POST['late_night']

        risk_score = calculate_risk(age, smoking, fitness, late_night, accidents)

        input_data = pd.DataFrame([[age, income, dependents, smoking, fitness, driving_km, late_night, accidents, risk_score]],
            columns=['Age', 'Annual_Income', 'Dependents', 'Smoking_Habit', 'Physical_Fitness', 'Daily_Driving_KM', 'Late_Night_Driving', 'Accident_History', 'Risk_Score'])

        for col in ['Smoking_Habit', 'Physical_Fitness', 'Late_Night_Driving']:
            input_data[col] = le_dict[col].transform(input_data[col])

        pred = model.predict(input_data)
        policy = le_dict['Target'].inverse_transform(pred)[0]

        profile, created = UserProfile.objects.get_or_create(user=request.user)
        profile.last_risk_score = risk_score
        profile.last_recommended_policy = policy
        profile.save()

        InsuranceHistory.objects.create(
            user=request.user,
            age=age,
            income=income,
            risk_score=risk_score,
            recommended_policy=policy
        )

        agents = InsuranceAgent.objects.filter(policy_name=policy)
        
        # নতুন: ইনপুট ডেটাসহ রেজাল্ট পেজে পাঠানো
        context = {
            'age': age, 'income': income, 'dependents': dependents,
            'driving_km': driving_km, 'accidents': accidents,
            'smoking': smoking, 'fitness': fitness, 'late_night': late_night,
            'risk_score': risk_score, 'policy': policy, 'agents': agents,
            'is_new_prediction': True
        }
        return render(request, 'result.html', context)

    user_history = InsuranceHistory.objects.filter(user=request.user).order_by('-date_saved')
    return render(request, 'index.html', {'history': user_history})

@login_required(login_url='login_page')
def delete_history(request, id):
    history_item = InsuranceHistory.objects.get(id=id, user=request.user)
    history_item.delete()
    return redirect('home')

@login_required(login_url='login_page')
def view_history(request, id):
    history_item = InsuranceHistory.objects.get(id=id, user=request.user)
    agents = InsuranceAgent.objects.filter(policy_name=history_item.recommended_policy)
    
    # নতুন: হিস্ট্রি থেকে ডেটাসহ রেজাল্ট পেজে পাঠানো
    context = {
        'age': history_item.age,
        'income': history_item.income,
        'risk_score': history_item.risk_score,
        'policy': history_item.recommended_policy,
        'agents': agents,
        'date': history_item.date_saved,
        'is_new_prediction': False
    }
    return render(request, 'result.html', context)