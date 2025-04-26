import cv2
import easyocr
import mysql.connector

# Connect to the MySQL database
db = mysql.connector.connect(
    host="localhost",  # Your host, e.g., "localhost"
    user="root",  # Your MySQL username
    password="root",  # Your MySQL password
    database="number_plates_db"  # The database name
)

cursor = db.cursor()

# Load the pre-trained Haar Cascade for number plates
plate_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_russian_plate_number.xml')

# Path to the downloaded video file
video_path = 'C:/Users/maury/Downloads/mini_clip.mp4'  # Replace with the actual video file path

# Initialize video capture
cap = cv2.VideoCapture(video_path)

# Initialize the EasyOCR reader
reader = easyocr.Reader(['en'])

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # Convert frame to grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect number plates in the frame
    plates = plate_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    # Draw rectangles around detected plates and store them in the database
    for (x, y, w, h) in plates:
        # Draw the rectangle
        cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)

        # Extract the detected plate region
        plate_region = frame[y:y + h, x:x + w]

        # Use EasyOCR to detect the text from the plate region
        detected_plate_number = reader.readtext(plate_region)

        if detected_plate_number:
            # Extract the text detected by EasyOCR
            detected_plate_number = detected_plate_number[0][1].strip()  # Clean up the string

            # Insert detected plate into the database
            cursor.execute("INSERT INTO vehicles (number_plates) VALUES (%s)", (detected_plate_number,))
            db.commit()

    # Display the frame with detected plates
    cv2.imshow('Number Plate Detection', frame)

    # Break loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release video capture and close any OpenCV windows
cap.release()
cv2.destroyAllWindows()

# Close the database connection
cursor.close()
db.close()
