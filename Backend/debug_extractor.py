from Backend.GoalExtractor import GoalExtractor

e = GoalExtractor()

print("--- DEBUG SCRIPT ---")

g1 = e.extract_goal("send message to mum")
print(f"1. send message to mum -> {g1}")

g2 = e.extract_goal("whatsapp brother")
print(f"2. whatsapp brother -> {g2}")

g3 = e.extract_goal("text boss")
print(f"3. text boss -> {g3}")

g4 = e.extract_goal("message random person")
print(f"4. random -> {g4}")
