## QuizCraft is a software that helps in Quiz Management for an organization or for personal use. 
This serves as a study tool to prepare well for examinations. It offers an interactive and growing environment for users/students to take quizzes and track their progress. 
An administrator manages all the subjects, quizzes and users.

--> STEPS TO RUN THIS LOCALLY

1. clone the repo

```bash
git clone https://github.com/dumaloocancode/QuizMaster.git
```

2. create a virtual environment

```bash
python -m venv .venv
```

3. navigate to the .venv folder and activate the environment

```bash
cd .venv
.\Scripts\activate
```

4. navigate to the main folder i.e. QuizCraft

```bash
cd ..
```

5. install dependencies

```bash
pip install -r requirements.txt
```

6. run the application

```bash
python main.py
```