from typing import assert_never
from rich.console import Console

console = Console()
questions = [
    ("question1",["A) 10", "B) 20", "C) 15", "D) 12"], "B"),
    ("question2", ["A) 12", "B) 22", "C) 2", "D) 11"], "A"),
]

playing = True
while playing:
    answer_menu = input("1.play game \n2.exit game").strip()
    if answer_menu == "1":
        score = 0
        correct_count = 0
        for question, options, correct_answer in questions:
            for opt in options:
                print(opt)
            answer = input("Your Answer: ").strip().upper()
            if answer == correct_answer:
                score += 5
                correct_count += 1
                console.print("Correct", style="green")
            else:
                console.print("Incorrect", style="red")
        console.print(correct_count / len(questions) * 100, style="blue")
    elif answer_menu == "2":
        console.print("goodbye",style="red on black")
        playing = False