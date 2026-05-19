# Speed Clicker 🎮
*Last Updated: 20 May 2026*

An arcade-style reaction game where players tap glowing shapes to build combos and beat their high scores. Built as a full-stack application with a cross-platform frontend and a Python backend.


## 🌟 Play Now
No setup required! You can play the live versions of the game right now:
* 🌐 **Play on Web:** [speed-clicker-web.onrender.com](https://speed-clicker-web.onrender.com)
* 📱 **Download for Android (.apk):** [Download Here](https://expo.dev/accounts/jc_study/projects/frontend/builds/0ff740e2-21f9-49d3-b419-93f5f4d06179)

---

## 🚀 Tech Stack
* **Frontend:** React Native (Expo), TypeScript, Web Support
* **Backend:** Python, FastAPI, Uvicorn
* **Database:** MongoDB (via Motor)

---

## 🛠️ Local Development Setup

Want to run the code on your own machine? Follow these steps to set up the local development environment.

.
### 1. Backend Setup
1. Open a new terminal and navigate to the backend folder:
   ```
   cd app/backend
   ```
2. Create and activate a virtual environment:
   ```
   python -m venv venv
	.\venv\Scripts\activate
   ```
3. Install dependencies:
   ```
   python -m pip install -r requirements.txt
   ```  
4. Start the server and leave the server active:
   ```
   python server.py
   ```
   or
   ```
   python -m uvicorn server:app --reload
   ```
   
.  
### 2. Frontend Setup
1. Open a new terminal and navigate to the frontend folder:
   ```
   cd app/frontend
   ```
2. Install the Node modules:
   ```
   npm install
   ```
3. Configure your local network IP in the "\app\frontend\.env" file:
   ```
   EXPO_PUBLIC_API_URL=http://<YOUR_LOCAL_IP>:8000
   ```
4. Start the Expo development server:
   ```
   npx expo start -c
   ```   

.
### 3. 📱 How to Test
1. Download the Expo Go app on your iOS or Android device.
2. Ensure your phone and computer are on the same Wi-Fi network.
3. Scan the QR code generated in your frontend terminal to launch the game.