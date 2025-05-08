import random
import pandas as pd
import matplotlib.pyplot as plt

# Step 1: Build a bank of 100 AP US History questions (placeholder for real questions)
quiz_bank = [
    {"question": f"Sample Question {i+1}", "options": ["A", "B", "C", "D"], "answer": random.choice(["A", "B", "C", "D"])}
    for i in range(100)
]

# Step 2: Generate multiple quiz batches
def generate_quiz_batches(bank, num_batches=10, batch_size=10):
    batches = []
    for _ in range(num_batches):
        batch = random.sample(bank, batch_size)
        batches.append(batch)
    return batches

# Step 3: Simulate LLM answering the quizzes (bias toward correct ~80%)
def simulate_llm_answers(batch):
    results = []
    correct_count = 0
    for q in batch:
        # Simulate ~80% accuracy by biasing towards the correct answer
        if random.random() < 0.8:
            simulated_answer = q['answer']
        else:
            simulated_answer = random.choice([opt for opt in ["A", "B", "C", "D"] if opt != q['answer']])
        is_correct = simulated_answer == q['answer']
        results.append({
            "question": q['question'],
            "correct_answer": q['answer'],
            "llm_answer": simulated_answer,
            "is_correct": is_correct
        })
        if is_correct:
            correct_count += 1
    accuracy = correct_count / len(batch)
    return results, accuracy

# Step 4: Run simulation and collect results
summary_data = []
all_results = []

batches = generate_quiz_batches(quiz_bank)
for i, batch in enumerate(batches):
    simulated_results, accuracy = simulate_llm_answers(batch)
    all_results.extend(simulated_results)
    summary_data.append({
        "batch_number": i + 1,
        "num_questions": len(batch),
        "num_correct": int(accuracy * len(batch)),
        "accuracy_percent": round(accuracy * 100, 2)
    })

summary_df = pd.DataFrame(summary_data)
results_df = pd.DataFrame(all_results)

# Step 5: Save to CSV files
summary_df.to_csv("/mnt/data/llm_evaluation_summary_high_accuracy.csv", index=False)
results_df.to_csv("/mnt/data/llm_detailed_results_high_accuracy.csv", index=False)

# Step 6: Create charts
plt.figure(figsize=(10, 6))
plt.bar(summary_df['batch_number'], summary_df['accuracy_percent'], color='lightgreen')
plt.xlabel('Batch Number')
plt.ylabel('Accuracy (%)')
plt.title('Simulated LLM Accuracy Across Quiz Batches (High Accuracy)')
plt.ylim(0, 100)
plt.xticks(summary_df['batch_number'])
plt.grid(axis='y', linestyle='--', alpha=0.7)
plt.tight_layout()
plt.savefig("/mnt/data/llm_high_accuracy_chart.png")

import ace_tools as tools; tools.display_dataframe_to_user(name="LLM Evaluation Summary (High Accuracy)", dataframe=summary_df)