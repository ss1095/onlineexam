# In views.py, implement registration and login views
import random

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('exam_list')  # Redirect to exam list page
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Exam, Question, StudentExam
from django.shortcuts import get_object_or_404


@login_required
def create_exam(request):
    if request.method == 'POST':
        title = request.POST['title']
        description = request.POST['description']
        duration = request.POST['duration']

        exam = Exam.objects.create(
            title=title,
            description=description,
            duration=duration,
        )
        return redirect('exam_list')  # Redirect to exam list page
    return render(request, 'create_exam.html')


@login_required
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == 'POST':
        question_text = request.POST['question_text']
        answer_a = request.POST['answer_a']
        answer_b = request.POST['answer_b']
        answer_c = request.POST['answer_c']
        answer_d = request.POST['answer_d']
        correct_answer = request.POST['correct_answer']

        Question.objects.create(
            exam=exam,
            question_text=question_text,
            answer_a=answer_a,
            answer_b=answer_b,
            answer_c=answer_c,
            answer_d=answer_d,
            correct_answer=correct_answer,
        )
        return redirect('exam_detail', exam_id=exam.id)  # Redirect to exam detail page
    return render(request, 'add_question.html', {'exam': exam})
from django.utils import timezone

@login_required
def take_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    questions = list(exam.questions.all())  # Convert to a list for randomization
    random.shuffle(questions)

    if request.method == 'POST':
        score = 0
        for question in questions:
            answer = request.POST.get(f'question_{question.id}')
            if answer == question.correct_answer:
                score += 1

        student_exam = StudentExam.objects.create(
            student=request.user,
            exam=exam,
            score=score,
            completed_at=timezone.now()
        )
        return redirect('exam_results', student_exam_id=student_exam.id)

    return render(request, 'take_exam.html', {'exam': exam, 'questions': questions})

@login_required
def exam_results(request, student_exam_id):
    student_exam = get_object_or_404(StudentExam, id=student_exam_id)
    return render(request, 'exam_results.html', {'student_exam': student_exam})
@login_required
def exam_performance(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    results = StudentExam.objects.filter(exam=exam)

    scores = [result.score for result in results]
    average_score = sum(scores) / len(scores) if scores else 0

    return render(request, 'exam_performance.html', {
        'exam': exam,
        'results': results,
        'average_score': average_score,
    })

# Create your views here.
