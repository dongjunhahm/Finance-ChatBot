from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/ask', methods=['POST'])
def ask(): 
    question = request.json.get('question')
    return jsonify({"answer": "mock answer"})

if __name__ == '__main__': 
    app.run(debug=True)