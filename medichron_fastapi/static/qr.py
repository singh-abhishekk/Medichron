import cv2
import pyzbar.pyzbar as pyzbar

# Open the default camera
cap = cv2.VideoCapture(0)

# Keep track of detected QR codes
detected_qr_codes = set()

while True:
    # Read the current frame from camera
    _, frame = cap.read()

    # Use pyzbar to decode any QR codes in the frame
    decoded_objs = pyzbar.decode(frame)

    # Loop over all the detected QR codes
    for decoded_obj in decoded_objs:
        # Extract the QR code's data
        data = decoded_obj.data.decode('utf-8')
        if data not in detected_qr_codes:
            # Print the QR code's data if it hasn't been printed already
            print(f"Found QR code: {data}")
            cv2.destroyAllWindows()
            cap.release()
            exit()

    # Show the frame
    cv2.imshow('QR Code Reader', frame)

    # Check for the 'q' key to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the camera and close the window
cap.release()
cv2.destroyAllWindows()