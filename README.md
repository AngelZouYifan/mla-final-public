# mla-final-public

### **README.md**

---

## **Self-Surveillance  App**

The Self-Surveillance App is a data visualization tool for analyzing app usage patterns on macOS, iOS, and iPadOS devices. 
It uses data extracted from `knowledgeC.db`, an internal system database that logs app activity on macOS. 

This Web App demonstrates with existing data: https://mla-final-public-l93lvdlnigqfrxx7rybwkd.streamlit.app/
You can follow this guide to extract your own data and visualize it.
---

## **Steps to Use**

### **1. Locate `knowledgeC.db`**
1. Open **Terminal** on your Mac.
2. Run the following command to navigate to the database location:
   ```bash
   cd ~/Library/Application\ Support/Knowledge

   ```
   For alternative, navigate using Finder.
3. Copy `knowledgeC.db` to a safe location (e.g., your desktop):
   ```bash
   cp knowledgeC.db ~/Desktop/
   ```

---

### **2. Extract Data from `knowledgeC.db`**
Use the provided Python script to extract relevant data into a CSV file:
1. Ensure Python 3.x is installed.
2. Run the script:
   ```bash
   python extract_knowledgeC.py -o <filename.csv>
   ```
   This will generate an output file `filename.csv`. If no argument is passed, the default output file is `output.csv`.

---


### **3. Local Deployment**
To run the app locally:
1. Clone the repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the app:
   ```bash
   streamlit run app.py
   ```
