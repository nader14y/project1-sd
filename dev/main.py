questions = [
    ("The best CMS in the World?", ["A: WordPress", "B: Joomla", "C: Drupal", "D: Squarespace"], "A"),
    ("What is the most popular CMS?", ["A: WordPress", "B: Joomla", "C: Drupal", "D: Squarespace"], "A"),
    ("Which CMS is known for its user-friendly interface?", ["A: WordPress", "B: Joomla", "C: Drupal", "D: Squarespace"], "A")
]

for question, answers, correct in questions:
    print(question)
    for answer in answers:
        print(f"{answer}\n")
    user_answer = input("Your answer (A/B/C/D): ").strip().upper()
    if user_answer == correct:
        print("Correct!\n")
    else:
        print(f"Wrong! The correct answer is {correct}.\n")