from rich.console import Console

questions = [
    ("The best CMS in the World?", ["A: WordPress", "B: Joomla", "C: Drupal", "D: Squarespace"], "A"),
    ("What is the most popular CMS?", ["A: WordPress", "B: Joomla", "C: Drupal", "D: Squarespace"], "A"),
    ("Which CMS is known for its user-friendly interface?", ["A: WordPress", "B: Joomla", "C: Drupal", "D: Squarespace"], "A")
]

console = Console() 

score = 0
total_correct = 0
CORRECT_BONES = 10
PENALTY = 3
for question, options, correct in questions:
    console.print(question, style="bold yellow")
    for option in options:
        console.print(f"{option}\n", style="bold cyan")
    user_answer = input("Your answer (A/B/C/D): ").strip().upper()
    if user_answer == correct:
        total_correct += 1
        score += CORRECT_BOUNES
        console.print("Correct!\n", "#ffccbb")
    else:
        score -= PENALTY
        console.print(f"Wrong! The correct answer is {correct}.\n", "bold red")
        
console.print(f"Your Score is: {score}", "bold green")
console.print(f"Total Correct answer: {total_correct}", "bold green")