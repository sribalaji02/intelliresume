from django.shortcuts import render
import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from tinydb import TinyDB, Query
import google.generativeai as palm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
context=""
db = TinyDB('db.json')
resume_metadata = TinyDB('resume_meta.json')

palm.configure(api_key="AIzaSyBbpCwN1__6EM1pmud37H_BqYVgWK9C0pI")

cred = credentials.Certificate("cred.json")
firebase_admin.initialize_app(cred)

def signup(request):

    try:
        email = request.POST['email']
        uname = request.POST['uname']
        request.session['email'] = email
        request.session['uname'] = uname

        password = request.POST['password']
        user = auth.create_user(
        email=email,
        password = password,
        display_name=uname,
        )
        db.insert({'uid': user.uid, 'pass': password})

        return render(request, "index.html")
    
    except:
        print(f"Error retrieving user")
        return render(request, "index.html")

def login(request):

    return render(request, "index.html")

def validate(request):
    
    email = request.POST['email']
    password = request.POST['password']
    user = auth.get_user_by_email(email)
    User = Query()
    pwd = db.search(User.uid == user.uid)
    request.session['email'] = email
    request.session['uname'] = user.display_name
    if user and user.email == email and pwd[0]["pass"] == password:
        return HttpResponseRedirect(reverse('home', kwargs={'uname': user.display_name}))
    
    else:
        return HttpResponseRedirect(reverse('login'))
    
def home(request, uname):

    return render(request, "home.html", {"username":uname})

def res(request, uname):
    try:
        jd = request.POST['jd']
        name = request.POST['name']
        phone = request.POST['phone']
        location = request.POST['location']
        email = request.POST['email']
        linkedin = request.POST['linkedin']
        github = request.POST['github']
        summary = request.POST['summary']
        work = request.POST['work']
        skills = request.POST['skills']
        education = request.POST['education']
        projects = request.POST['projects']
        certifications = request.POST['certifications']

        cur_skills = f"""Generate skills that are required for this company that I'm currently applying for : 
                        {jd},
                        The skillset that I have currently are :
                        {skills},
                        Please create a correct skillset for me to put in my skills using the above mentioned skills only for my Resume that I'm creating. NOTE: ONLY WITH THE SKILLS I GAVE YOU THAT I HAD NOT ANYTHING EXTRA. ALSO MAKE SURE NOT TO MAKE ANYTHING BOLD OR ITALICS AND GIVE ONLY IN POINTS.
                        """
        upd_skills = generate(cur_skills)

        cur_summary = f"""Generate job summary that is required for this company that I'm currently applying for : 
                        {jd},
                        The job summary that I have entered is :
                        {summary},
                        Please create a professional, 'short job summary' for me to put in my Job Summary/ Job description tab in my Resume that I'm creating. NOTE GIVE ONLY 10 LINES OF DESCRIPTION.
                        """
        upd_summary = generate(cur_summary)

        cur_proj = f"""Generate Project summary that are required for this company that I'm currently applying for : 
                        {jd},
                        The Project summary that I have entered is :
                        {projects},
                        Please create a professional, project description presumably in points for me to put in my projects that I have worked on in my Resume that I'm creating, also make it emphasizing : MY ROLE IN IT, NEED FOR THIS PROJECT, FUTURE OF THIS PROJECT, HOW THIS AFFECTS THE CURRENT PERIOD.
                        """
        upd_proj = generate(cur_proj)
        email = request.session.get('email')
        
        User = Query()
        resume_metadata.clear_cache()
        resume_metadata.remove(User.email == email)

        resume_metadata.insert({'email': email, 'name':name, 'phone':phone, 'location':location, 'linkedin':linkedin, 'github':github, 'summary':upd_summary, 'work':work, 'skills':upd_skills, 'education':education,
                   'projects':upd_proj, 'certifications':certifications})
        
        request.session['email'] = email
        return HttpResponseRedirect(reverse('resgen', kwargs={'uname': uname}))

    except:
        return render(request, "details.html", {'uname':uname})

def resgen(request, uname):

    email = request.session.get('email')
    User = Query()
    obj = resume_metadata.search(User.email == email)
    print(obj)
    return render(request, 'resume.html', {'uname':uname, 'name':obj[0]['name'], 'phone':obj[0]['phone'], 'location':obj[0]['location'], 'linkedin':obj[0]['linkedin'], 
                                           'github':obj[0]['github'], 'email':obj[0]['email'], 'summary':obj[0]['summary'], 'work':obj[0]['work'], 'skills':obj[0]['skills'],
                                           'proj':obj[0]['projects'], 'cert':obj[0]['certifications']})


    #Check user commands
    # user =  auth.get_user_by_email("user@gmail.com")
    # print("Successfully retrieved user:")
    # print(f"UID: {user.uid}")
    # print(f"Email: {user.email}")
    # print(f"Display Name: {user.display_name}")


    # user = auth.create_user(
    # email="user@gmail.com",
    # password="123456",
    # display_name="John Doe",
    # )

    # print(f"Successfully created user: {user.uid}")

def generate(input_data):
    response = palm.chat(messages="Hello")

    response = response.reply(input_data)

    return response.last

def chat_msg(prompt):
    defaults = {
        'model': 'models/chat-bison-001',
        'temperature': 0.25,
        'candidate_count': 1,
        'top_k': 40,
        'top_p': 0.95,
    }
    def gen_msg(new_message):
        global context
        examples = []
        messages = []

        print("AI is thinking...", end="", flush=True)
        messages.append(new_message)
        conversation_history = context + f"Human: {new_message}\n"
        response = palm.chat(
            **defaults,
            context=context,
            examples=examples,
            messages=messages
        )
        
        ai_response = response.last
        context = conversation_history + f"AI: {ai_response}\n"
        print(ai_response)
        return ai_response

    return gen_msg(prompt)

@csrf_exempt
def chat(request, uname):
    global context
    if request.method == 'GET':
        context = ""
    if request.method == 'POST':
        user_message = request.POST.get('chat', '')
        bot_response = chat_msg(user_message)
        return JsonResponse({'bot': bot_response})

    return render(request, "chat.html", {'uname':uname})


