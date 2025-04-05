## QuizCraft is an application that helps in Quiz Management for an organization or for personal use. An admin can create and manage subjects, chapters and quizzes for chapters, as well as users of their organization. The admin can create questions and options for a particular quiz. A user is able to see all the subjects, chapters and quizzes. The user can attempt any quiz of any chapter of their choice. 

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