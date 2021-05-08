import face_recognition
import os
import cv2
import PIL
import pickle
import time
import subprocess

KNOWN_FACES_DIR = 'known_faces'
TOLERANCE = 0.56 
FRAME_THICKNESS = 2
FONT_THICKNESS = 1
MODEL = 'hog'  # default: 'hog', other one can be 'cnn'
capture_duration = 10

index1 = open("index.txt","r")
index_id = index1.read()
index1.close()
next_id = index_id
match = None
print('Get ready for Face Detection...')
known_faces = []
known_names = []


start_time = time.time()


class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        try:
            success, image = self.video.read()

            locations = face_recognition.face_locations(image, model=MODEL)  # finds the location points for face in the frame

            encodings = face_recognition.face_encodings(image, locations) # Generates encoding: mapping of different features on the face
            #check.
            for face_encoding, face_location in zip(encodings, locations):
                top_left = (face_location[3], face_location[0])
                bottom_right = (face_location[1], face_location[2])

                color = (0, 0, 0)
                # Paint frame
                cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

                    # Now we need smaller, filled grame below for a name
                    # This time we use bottom in both corners - to start from bottom and move 50 pixels down
                top_left = (face_location[3], face_location[2])
                bottom_right = (face_location[1], face_location[2] + 22)

                    # Paint frame
                cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)

                    # Wite a name
                cv2.putText(image, str(next_id)+"-B", (face_location[3] + 3, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), FONT_THICKNESS)

                if os.path.exists(f"{KNOWN_FACES_DIR}/{next_id}-B"): #If an ID is generated for the user
        
                    results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE) #compare previous encodings to current encoding generated

                    if True in results: # If it is a match : do nothing
                        break
                    else: # If it is not a match: store the new encoding and append to known faces list
                        pickle.dump(face_encoding, open(f"{KNOWN_FACES_DIR}/{next_id}-B/{next_id}-A-{int(time.time())}.pkl", "wb"))
                        known_faces.append(face_encoding)
                        #print(face_encoding)
                else: # If ID is not generated: Generated ID and create folder with ID as name
                    os.mkdir(f"{KNOWN_FACES_DIR}/{next_id}-B") 
                    pickle.dump(face_encoding, open(f"{KNOWN_FACES_DIR}/{next_id}-B/{next_id}-A-{int(time.time())}.pkl", "wb")) #Store the encoding
                    known_faces.append(face_encoding) # Append to known faces list
                print (known_faces)
                
            if len(known_faces) < 1:
                print('Face not detected')
                
            else:
                index_id = int(next_id) + 1
                index1 = open("index.txt", "w")
                index1.write(str(index_id))
                index1.close()

                
            ret, jpeg = cv2.imencode('.jpg', image)
            
            if len(known_faces)<1:
                raise Exception("Face not detected")
            return jpeg.tobytes()
        except:
            index_id = int(next_id)
            index1 = open("index.txt", "w")
            index1.write(str(index_id))
            index1.close()
            return jpeg.tobytes()
            
    

class VideoCamera1(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
    
    def __del__(self):
        self.video.release()
    
    def get_frame(self):
        
        for name in os.listdir(KNOWN_FACES_DIR):

            # Next we load every file of faces of known person
            for filename in os.listdir(f'{KNOWN_FACES_DIR}/{name}'):
        
                with open(f'{KNOWN_FACES_DIR}/{name}/{filename}',"rb") as picklefile:
                    encoding = pickle.load(picklefile)
                # Append encodings and name
                known_faces.append(encoding)
                known_names.append(str(name))
        start_time = time.time()
        #while ( int(time.time() - start_time) < capture_duration ):
        try:
            success, image = self.video.read()
   
            locations = face_recognition.face_locations(image, model=MODEL)

            encodings = face_recognition.face_encodings(image, locations)

            for face_encoding, face_location in zip(encodings, locations):

                results = face_recognition.compare_faces(known_faces, face_encoding, TOLERANCE)

                match = None
                if True in results:  # If at least one is true, get a name of first of found labels
                    match = known_names[results.index(True)]
                    
                #    #print(f' - {match} from {results}')
                elif match == None:
                    raise Exception("Could not find a match")
                    

                result = str(match)
                res = open("result.txt","w")
                res.write(str(result))
                res.close()
                
                # Each location contains positions in order: top, right, bottom, left
                top_left = (face_location[3], face_location[0])
                bottom_right = (face_location[1], face_location[2])

                    # Get color 
                color = (0, 0, 0)

                    # Paint frame
                cv2.rectangle(image, top_left, bottom_right, color, FRAME_THICKNESS)

                    # Now we need smaller, filled grame below for a name
                    # This time we use bottom in both corners - to start from bottom and move 50 pixels down
                top_left = (face_location[3], face_location[2])
                bottom_right = (face_location[1], face_location[2] + 22)

                    # Paint frame
                cv2.rectangle(image, top_left, bottom_right, color, cv2.FILLED)

                    # Wite a name
                cv2.putText(image, str(match), (face_location[3] + 3, face_location[2] + 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), FONT_THICKNESS)        
                
                #result = str(match)
                #res = open("result.txt","w")
                #res.write(str(result))
                #res.close()
                ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
        except:
            match = 0
            result = str(match)
            res = open("result.txt","w")
            res.write(str(result))
            res.close()
            ret, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()