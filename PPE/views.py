import pygame, torch
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Student, UploadedVideo
import cv2, os, io, time, threading, csv, smtplib
from django.http import StreamingHttpResponse, JsonResponse, HttpResponse
from ultralytics import YOLO
from django.conf import settings
from email.message import EmailMessage
from django.views.decorators.csrf import csrf_protect

def landing(request):
    return render(request,'PPE-3.1.html')
def exit(request):
    return render(request, 'exit.html')
def graphs(request):
    return render(request, 'graphs.html')
def datasets(request):
    return render(request, 'datasets.html')

def userRegister(request):
    if request.method == 'POST':
        studentname = request.POST.get('studentname', '').strip()
        email = request.POST.get('email', '').strip()
        mobile = request.POST.get('mobile', '').strip()
        password = request.POST.get('password', '').strip()
        status = request.POST.get('status', '').strip()

        if Student.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'userRegister.html')
        user = Student(studentname=studentname, email=email, mobile=mobile, password=password, status=status)
        user.save()
        # return render(request, 'userlogin.html')
        return redirect('/userlogin')
    return render(request, 'userRegister.html')
def userlogin(request):
    if request.method == 'POST':
        studentname = request.POST.get('studentname')
        password = request.POST.get('password')
        try:
            user = Student.objects.get(studentname=studentname)
            if user.password == password:
                # Check if the account is still waiting for activation
                if user.status == "Waiting":
                    messages.info(request,
                                  "Your account status is currently Waiting. Please wait until it is activated by Admin.")
                    return render(request, 'userlogin.html')

                # Store user ID in session to persist across views
                request.session['user_id'] = user.id

                # Redirect to userhome without using GET parameters
                return redirect('/userhome')

            else:
                messages.error(request, "Invalid UserName or Password!")
                return render(request, 'userlogin.html')

        except Student.DoesNotExist:
            messages.error(request, "UserName or Password is Incorrect")
            return render(request, 'userlogin.html')

    return render(request, 'userlogin.html')
def userhome(request):
    # Retrieve user ID from session
    user_id = request.session.get('user_id')
    if not user_id:
        messages.error(request, "Unauthorized access. Please log in.")
        return redirect('userlogin')
    # Fetch student details based on ID
    student = Student.objects.filter(id=user_id).first()
    return render(request, 'userhome.html', {'studentdetails': student})

def adminlogin(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        password = request.POST.get('password')
        try:
            if name == 'admin' and password == 'admin':

                # Store user ID in session to persist across views
                return redirect('/adminhome')
            else:
                messages.error(request, "Invalid UserName or Password!")
                return render(request, 'adminlogin.html')
        except Student.DoesNotExist:
            messages.error(request, "UserName or Password is Incorrect")
            return render(request, 'adminlogin.html')
    return render(request, 'adminlogin.html')
def adminhome(request):
    user = Student.objects.all()
    return render(request, 'adminhome.html', {'userdetails': user})

def activateuser(request):
    # print(request.GET)
    id = request.GET.get('id')
    ur = Student.objects.get(id=id)
    ur.status = 'Active'
    ur.save()
    return redirect('/adminhome')
def deactivateuser(request):
    # print(request.GET)
    id = request.GET.get('id')
    ur = Student.objects.get(id=id)
    ur.status = 'Waiting'
    ur.save()
    return redirect('/adminhome')
def deleteuser(request):
    # print(request.GET)
    id = request.GET.get('id')
    ur = Student.objects.get(id=id)
    ur.delete()
    return redirect('/adminhome')

# Load YOLOv8 model
model = YOLO("best-git.pt")  # Use the appropriate model path
# model = YOLO("/Users/chiru/PycharmProjects/PPEproject/best_saved_model/best_float32.tflite")

# Directory to store uploaded videos
UPLOAD_DIR = "media/uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

# Upload Video View
def upload_video(request):
    user_id = request.session.get('user_id')
    student = Student.objects.filter(id=user_id).first()
    if request.method == "POST" and request.FILES.get("video"):
        video = request.FILES["video"]
        uploaded_video = UploadedVideo.objects.create(video=video)
        return redirect("detect_video", id=uploaded_video.id)
    return render(request, "upload.html",{'studentdetails': student})

def detect_video(request, id):
    print("Received ID in video_view:", id)
    video = UploadedVideo.objects.get(id=id)
    return render(request, "detect.html", {"video": video})


pygame.mixer.init()
# Video Processing for Detection
def play_sound_alert():
    sound_path = "media/buzzer.mp3"
    pygame.mixer.music.load(sound_path)
    pygame.mixer.music.play()

def video_processing(video_path, email):
    cap = cv2.VideoCapture(video_path)
    last_otp_time = 0  # Track the last time OTP was sent
    otp_interval = 20  # OTP interval in seconds

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        results = model(frame)
        annotated_frame = results[0].plot()
        violation_detected = False  # Track if a violation is detected in this frame

        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            class_name = model.names[cls_id]

            if class_name in ['NO-Safety Vest', 'NO-Mask', 'No-Helmet']:
                play_sound_alert()
                violation_detected = True
                break  # No need to check further boxes for this frame

        # Send OTP if a violation is detected and enough time has passed
        if violation_detected:
            current_time = time.time()
            if current_time - last_otp_time >= otp_interval:
                otp(email)
                last_otp_time = current_time

        _, buffer = cv2.imencode(".jpg", annotated_frame)
        frame_bytes = buffer.tobytes()

        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

    cap.release()

# Stream Processed Video
def video_feed(request, id):
    user_id = request.session.get('user_id')
    student_email = Student.objects.filter(id=user_id).values_list('email', flat=True).first()  # Get email
    video = UploadedVideo.objects.get(id=id)
    video_path = os.path.join(settings.MEDIA_ROOT, str(video.video))
    return StreamingHttpResponse(video_processing(video_path, student_email), content_type="multipart/x-mixed-replace; boundary=frame")

# Live Webcam Detection
def live_camera(request):
    user_id = request.session.get('user_id')
    student_email = Student.objects.filter(id=user_id).values_list('email', flat=True).first()  # Get email
    camera_index = request.GET.get("camera", 0)  # Get camera index from request
    video_feed_url = f"/live_feed_solo/?camera={camera_index}&email={student_email}"
    return render(request, "live.html", {"video_feed_url": video_feed_url, "student_email": student_email, "camera_index": camera_index})

def live_feed_solo(request):
    """Handles live-streaming of video with YOLOv8 detection"""
    camera_index = int(request.GET.get("camera", 0))  # Default to Camera 0
    student_email = request.GET.get("email")  # Get email from query params
    if not student_email:
        return JsonResponse({"error": "Email is required for OTP"}, status=400)  # Ensure email is provided

    cap = cv2.VideoCapture(camera_index)  # Open selected camera
    if not cap.isOpened():
        return JsonResponse({"error": "Camera not accessible"}, status=500)

    prev_time = time.time()  # Initialize FPS counter
    start_time = time.time()  # Timer for 5 seconds
    max_fps = 0  # Store max FPS

    def generate():
        nonlocal prev_time, start_time, max_fps
        last_otp_time = 0  # Track the last time OTP was sent
        otp_interval = 10  # OTP interval in seconds
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print("Error: Failed to capture frame.")
                    break

                # Calculate FPS
                curr_time = time.time()
                fps = 1 / (curr_time - prev_time) if prev_time else 0
                prev_time = curr_time

                # Update max FPS in the last 5 seconds
                max_fps = max(max_fps, fps)

                # Check if 5 seconds have passed
                if curr_time - start_time >= 1:
                    displayed_fps = max_fps  # Store max FPS to display
                    max_fps = 0  # Reset max FPS counter
                    start_time = curr_time  # Reset 5-second timer
                else:
                    displayed_fps = max_fps  # Keep displaying max FPS

                # Run YOLOv8 Object Detection
                results = model(frame)
                annotated_frame = results[0].plot()
                violation_detected = False  # Track if a violation is detected in this frame

                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    class_name = model.names[cls_id]

                    if class_name in ['NO-Safety Vest', 'NO-Mask', 'No-Helmet']:
                        play_sound_alert()
                        violation_detected = True
                        break  # No need to check further boxes for this frame

                # Send OTP if a violation is detected and enough time has passed
                if violation_detected:
                    current_time = time.time()
                    if current_time - last_otp_time >= otp_interval:
                        otp(student_email)
                        last_otp_time = current_time

                # Overlay Max FPS on the frame
                (text_width, text_height), _ = cv2.getTextSize(f"FPS : {displayed_fps:.2f}", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                frame_width = annotated_frame.shape[1]
                x = frame_width - text_width - 40  # 10 pixels from the right edge
                y = 50  # Keep it at the same height
                # Draw a filled rectangle for the background
                rect_width, rect_height = cv2.getTextSize(f"FPS : {displayed_fps:.2f}", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                rect_x, rect_y = x - 10, y - 30
                cv2.rectangle(annotated_frame, (rect_x, rect_y), (rect_x + rect_width + 20, rect_y + rect_height + 20), (0, 0, 255), -1)

                # Now overlay the text on top of the rectangle
                cv2.putText(annotated_frame, f"FPS : {displayed_fps:.2f}", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

                # Convert frame to bytes
                _, buffer = cv2.imencode(".jpg", annotated_frame)
                frame_bytes = buffer.tobytes()

                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" +
                       frame_bytes + b"\r\n")

        except GeneratorExit:
            print("Client Disconnected, Stopped Camera...")
        finally:
            cap.release()  # Ensure camera is released when stream stops

    return StreamingHttpResponse(generate(), content_type="multipart/x-mixed-replace; boundary=frame")

# Multi Live Threads
class camThread(threading.Thread):
    def __init__(self, previewName, camID, generate_func):
        threading.Thread.__init__(self)
        self.previewName = previewName
        self.camID = camID
        self.generate_func = generate_func

    def run(self):
        print("Starting " + self.previewName)
        camPreview(self.previewName, self.camID, self.generate_func)

def camPreview(previewName, camID, generate_func):
    global frame
    cv2.namedWindow(previewName)
    cam = cv2.VideoCapture(camID)
    if cam.isOpened():  # Try to get the first frame
        rval, frame = cam.read()
    else:
        rval = False

    while rval:
        cv2.imshow(previewName, frame)
        rval, frame = cam.read()
        generate_func(frame)
        key = cv2.waitKey(20)
        if key == 27:  # Exit on ESC
            break
    cv2.destroyWindow(previewName)

def get_available_cameras(max_index=10):
    """ Check for available camera indices up to `max_index`. """
    available_cameras = []
    for i in range(max_index):
        cap = cv2.VideoCapture(i)
        if cap.isOpened():
            available_cameras.append(i)
            cap.release()  # Release the camera after checking
    return available_cameras
def live_feed_page(request):
    """ Render the live feed page with dynamically available cameras and student email. """
    cameras = get_available_cameras()
    return render(request, "live_feed.html", {"cameras": cameras})

def live_feed(request, camera_index):
    """Handles live-streaming of video with YOLOv8 detection"""
    cap = cv2.VideoCapture(camera_index)  # Open selected camera
    if not cap.isOpened():
        return JsonResponse({"error": f"Camera {camera_index} not accessible"}, status=500)

    prev_time = time.time()  # Initialize FPS counter
    start_time = time.time()  # Timer for 5 seconds
    max_fps = 0  # Store max FPS

    def generate():
        nonlocal prev_time, start_time, max_fps
        try:
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    print(f"Error: Failed to capture frame from Camera {camera_index}.")
                    break

                # Calculate FPS
                curr_time = time.time()
                fps = 1 / (curr_time - prev_time) if prev_time else 0
                prev_time = curr_time

                # Update max FPS in the last 5 seconds
                max_fps = max(max_fps, fps)

                # Check if 5 seconds have passed
                if curr_time - start_time >= 1:
                    displayed_fps = max_fps  # Store max FPS to display
                    max_fps = 0  # Reset max FPS counter
                    start_time = curr_time  # Reset 5-second timer
                else:
                    displayed_fps = max_fps  # Keep displaying max FPS

                # Run YOLOv8 Object Detection
                results = model(frame)
                annotated_frame = results[0].plot()

                for box in results[0].boxes:
                    cls_id = int(box.cls[0])
                    class_name = model.names[cls_id]

                    if class_name in ['NO-Safety Vest', 'NO-Mask', 'No-Helmet']:
                        play_sound_alert()

                # Overlay Max FPS on the frame
                (text_width, text_height), _ = cv2.getTextSize(f"FPS : {displayed_fps:.2f}", cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                frame_width = annotated_frame.shape[1]
                x = frame_width - text_width - 40  # 10 pixels from the right edge
                y = 50  # Keep it at the same height

                cv2.putText(annotated_frame, f"FPS : {displayed_fps:.2f}", (x, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

                # Convert frame to bytes
                _, buffer = cv2.imencode(".jpg", annotated_frame)
                frame_bytes = buffer.tobytes()

                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" +
                       frame_bytes + b"\r\n")

        except GeneratorExit:
            print(f"Client Disconnected, Stopped Camera {camera_index}...")
        finally:
            cap.release()  # Ensure camera is released when stream stops

    return StreamingHttpResponse(generate(), content_type="multipart/x-mixed-replace; boundary=frame")

def display_csv(request):
    file_path = '/Users/chiru/PycharmProjects/PPEproject/media/train2/results.csv'
    data = []
    with open(file_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return render(request, 'display_csv.html', {"data": data})

def otp(email):
    def send_email():
        from_mail = 'chak7755@gmail.com'
        to_mail = email
        msg = EmailMessage()
        msg['subject'] = 'PPE SYSTEM ALERT'
        msg['from'] = from_mail
        msg['to'] = to_mail
        msg.set_content('PPE Guidelines Violation Detected')
        try:
            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(from_mail, 'hdyy zqsp bmha cyrn')
            server.send_message(msg)
            server.quit()
            print("Email sent successfully!")
        except smtplib.SMTPException as e:
            print(f"Failed to send email: {e}")
    # Start a new thread for sending the email
    threading.Thread(target=send_email).start()
    return True

# Global variables to control thread execution
training_thread = None
is_training_running = threading.Event()
# Global flag to control training
stop_training = threading.Event()

@csrf_protect
def stop_training_view(request):
    if request.method == 'POST':
        # Logic to stop training, e.g., stop the thread or set a flag
        return HttpResponse("Training stopped successfully.")
    return HttpResponse("Invalid request method.", status=400)

def run_training(output_buffer):
    # Load the YOLO model
    model = YOLO('yolov8n.pt')
    device = 'mps' if torch.backends.mps.is_available() else 'cpu'

    try:
        output_buffer.write("Training started...\n")
        for epoch in range(1, 2):  # Simulate one epoch
            if stop_training.is_set():
                output_buffer.write("Training stopped by user.\n")
                break

            # Train the model
            model.train(
                data='/Users/chiru/PycharmProjects/PPEproject/media/data.yaml',
                epochs=1, imgsz=640, verbose=True, stream_buffer=True, device=device
            )

        if not stop_training.is_set():
            output_buffer.write("Training completed and model saved.\n")
        model.save('best-model.pt')
    except Exception as e:
        output_buffer.write(f"Error during training: {str(e)}\n")
    finally:
        is_training_running.clear()  # Allow new training sessions
        stop_training.clear()  # Reset stop flag

# SSE Streaming function
def training_stream(request):
    global training_thread

    # If training is already running, return an immediate message
    if is_training_running.is_set():
        return HttpResponse("data: Training is already in progress. Please wait.\n\n", content_type='text/event-stream')

    output_buffer = io.StringIO()
    is_training_running.set()

    # Start the training in a separate thread
    training_thread = threading.Thread(target=run_training, args=(output_buffer,))
    training_thread.daemon = True  # Ensure the thread exits if the request ends
    training_thread.start()

    def stream_output():
        # Continuously read and yield new data from the buffer
        while is_training_running.is_set():
            output = output_buffer.getvalue()
            if output:
                yield f"data: {output}\n\n"  # SSE format
                output_buffer.truncate(0)  # Clear the buffer after sending
                output_buffer.seek(0)

    return StreamingHttpResponse(stream_output(), content_type='text/event-stream')

def command_view(request):
    return render(request, 'command_view.html')
