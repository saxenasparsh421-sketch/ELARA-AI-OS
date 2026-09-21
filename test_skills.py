from skills.loader import load_skills

print("===== Skills Loader =====\n")

skills = load_skills()

for skill in skills:
    print(skill.__name__)