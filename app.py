from flask import Flask, request, jsonify
from weather_agent import weather_agent

app = Flask(__name__)

# Принудительная установка UTF-8 для входящих и исходящих данных
app.config['JSON_AS_ASCII'] = False
app.config['JSON_SORT_KEYS'] = False

@app.before_request
def set_request_encoding():
    """Установка UTF-8 кодировки для входящих запросов"""
    if request.mimetype and 'charset' not in request.mimetype:
        request.environ['CONTENT_TYPE'] = 'application/json; charset=utf-8'

@app.after_request
def set_response_encoding(response):
    """Установка UTF-8 кодировки для исходящих ответов"""
    if response.content_type and 'charset' not in response.content_type:
        response.headers['Content-Type'] = f'{response.content_type}; charset=utf-8'
    return response


@app.route('/analyze', methods=['POST'])
def analyze():
    """Endpoint для анализа вопроса о погоде через weather_agent"""
    try:
        data = request.get_json()

        if not data or 'question' not in data:
            return jsonify({'error': 'Поле "question" обязательно'}), 400

        question = data['question'].strip()

        if not question:
            return jsonify({'error': 'Вопрос не может быть пустым'}), 400

        answer = weather_agent(question)

        return jsonify({
            'question': question,
            'answer': answer
        }), 200

    except Exception as e:
        return jsonify({'error': f'Ошибка при обработке запроса: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health():
    """Проверка статуса приложения"""
    return jsonify({'status': 'ok', 'service': 'weather_agent'}), 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
