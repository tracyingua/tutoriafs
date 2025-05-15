from tutoria_app.models import (
    StudentAssessmentResponse,
    TutorAssessmentResponse,
    TutorProfile,
    TutorAssessmentQuestion,
    TutorAnswerChoice
)

#ABLE TO ANALYZE THE ASSESSMENT OF TUTOR AND STUDENT
def get_matching_tutors(student):
    student_answers = StudentAssessmentResponse.objects.filter(student=student)
    tutor_matches = []


    for student_response in student_answers:
        print(f"  - {student_response.question.question_text}: {student_response.selected_answer.text}")

    for tutor in TutorProfile.objects.all():
        tutor_answers = TutorAssessmentResponse.objects.filter(tutor=tutor)
        matches = 0

      

        for student_response in student_answers:
     
            tutor_question = TutorAssessmentQuestion.objects.filter(
                linked_student_question=student_response.question
            ).first()

            if tutor_question:
                
                tutor_answer_choice = TutorAnswerChoice.objects.filter(
                    question=tutor_question, linked_student_answer=student_response.selected_answer
                ).first()

                if tutor_answer_choice and tutor_answers.filter(question=tutor_question, selected_answer=tutor_answer_choice).exists():
                    matches += 1
                    print(f"Match on: {student_response.question.question_text}")

        match_score = (matches / student_answers.count()) * 100 if student_answers.count() > 0 else 0

        tutor_matches.append({
            "tutor": tutor,
            "match_score": match_score
        })

    sorted_tutors = sorted(tutor_matches, key=lambda x: x["match_score"], reverse=True)

    for match in sorted_tutors:
        print(f"  - {match['tutor'].user.get_full_name()}: {match['match_score']}%")

    return sorted_tutors
