from datetime import datetime
from flask import Flask, request, jsonify, abort, render_template, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
import openai, json, traceback, requests

app = Flask(__name__)
app.config.from_object('config')
app.config['DEBUG'] = True 
db = SQLAlchemy(app) 

openai.api_key = app.config['OPEN_AI_KEY']

@app.route('/', methods=['GET'])
def root_get():
    return redirect(url_for('inspect'))

@app.route('/inspect')
def inspect():
    all_cards = AgricolaCard.query.with_entities(
        AgricolaCard.id, #0
        AgricolaCard.ext_id, #1
        AgricolaCard.row_id, #2
        AgricolaCard.card_title, #3
        AgricolaCard.base_expansion, #4
        AgricolaCard.deck, #5
        AgricolaCard.type, #6
        AgricolaCard.players, #7
        AgricolaCard.cost, #8
        AgricolaCard.vps, #9
        AgricolaCard.prerequisites, #10
        AgricolaCard.pass_left, #11
        AgricolaCard.category, #12
        AgricolaCard.text, #13
        AgricolaCard.insight, #14
        AgricolaCard.rating, #15
        AgricolaCard.improvement_complement, #16
        AgricolaCard.source).order_by(AgricolaCard.deck, AgricolaCard.card_title).all()
    cards_info = [
        {
            'title': card[3],
            'insight': card[14],
            'rating': card[15],
            'deck': card[5],
            'text': card[13],
            'cost': card[8],
            'category': card[12],
            'type': card[6],
            'players': card[7],
            'base_expansion': card[4],
            'vps': card[9],
            'improvement_complement': card[16],
            'id': card[1]
        }
        for card in all_cards
    ]
    return render_template('agricola_search.html', cards_info=cards_info)

@app.route('/search')
def search():
    query = request.args.get('query')
    filter_query = request.args.get('filter_query')  # Second query parameter

    results = AgricolaCard.query.filter(AgricolaCard.card_title.like(f'%{query}%'))
    if filter_query:
        results = results.filter(
            db.or_(
                AgricolaCard.type.like(f'%{filter_query}%'),
                AgricolaCard.category.like(f'%{filter_query}%'),
                AgricolaCard.deck.like(f'%{filter_query}%'),
                AgricolaCard.cost.like(f'%{filter_query}%'),
                AgricolaCard.base_expansion.like(f'%{filter_query}%')
            )
        )

    results = results.limit(10).all()
    titles = [result.card_title for result in results]
    return jsonify(matching_results=titles)

@app.route('/get-cards', methods=['GET'])
def get_cards():
    query = AgricolaCard.query

    filterable_columns = ['card_title', 'rating', 'insight', 'text', 'cost', 'type', 'category', 'base_expansion', 'vps', 'players', 'improvement_complement']
    for column in filterable_columns:
        if column in request.args and request.args.get(column) != '':
            value = request.args.get(column)
            if column == 'rating':
                # Convert to int only if value is not an empty string
                query = query.filter(getattr(AgricolaCard, column) == int(value))
            else:
                query = query.filter(getattr(AgricolaCard, column).like(f"%{value}%"))

    sort_column = request.args.get('sort', 'id')
    sort_order = request.args.get('order', 'asc')

    if sort_order == 'asc':
        query = query.order_by(getattr(AgricolaCard, sort_column).asc())
    else:
        query = query.order_by(getattr(AgricolaCard, sort_column).desc())

    cards = query.all()
    cards_list = [{column: getattr(card, column) for column in filterable_columns} for card in cards]

    return jsonify(cards_list)


@app.route('/list', methods=['GET'])
def list_cards():
    # Retrieve query parameters for filtering
    query = AgricolaCard.query
    filters = request.args

    for key, value in filters.items():
        if key in ['card_title', 'insight', 'text', 'cost', 'type', 'category', 'base_expansion', 'vps', 'players', 'improvement_complement'] and value:
            query = query.filter(getattr(AgricolaCard, key).like(f"%{value}%"))
        elif key == 'rating' and value:
            query = query.filter_by(rating=value)

    # Sorting
    sort_by = request.args.get('sort_by', 'id')
    if sort_by in ['card_title', 'rating', 'insight', 'text', 'cost', 'type', 'category', 'base_expansion', 'vps', 'players', 'improvement_complement']:
        query = query.order_by(getattr(AgricolaCard, sort_by))

    cards = query.all()
    return render_template('list-cards.html', cards=cards)

@app.route('/img')
def img():
    bypass_code = request.args.get('bypass')
    if bypass_code:
        # Redirect to the generate-image route with the bypass code
        return redirect(url_for('generate_image', bypass_code=bypass_code))
    return render_template('dall-e.html')

@app.route('/generate-image')
def generate_image():
    today = datetime.now().date()

    if 'last_access' in session and session['last_access'] == str(today):
        session['access_count'] = session.get('access_count', 0) + 1
    else:
        session['access_count'] = 1
        session['last_access'] = str(today)

    if session['access_count'] > 3:
        return jsonify({'error': 'Daily limit reached'}), 429  # HTTP 429 Too Many Requests

    response = openai.Image.create(
        model="dall-e-3",
        prompt="A farm, containing sheep, boar, cattle, and fields of wheat and carrots, resembling the board game Agricola. A small medieval village appears in the background as the sun sets.",
        size="1024x1024",
        n=1
    )
    image_url = response['data'][0]['url']
    return jsonify({'image_url': image_url})

class AgricolaCard(db.Model):
    __tablename__ = 'agricola_cards'
    id = db.Column(db.Integer, primary_key=True)
    ext_id = db.Column(db.Integer, unique=True)
    row_id = db.Column(db.Integer)
    card_title = db.Column(db.String(255))
    base_expansion = db.Column(db.String(255))
    deck = db.Column(db.String(255))
    type = db.Column(db.String(255))
    players = db.Column(db.String(2))
    cost = db.Column(db.String(255))
    vps = db.Column(db.String(5))
    prerequisites = db.Column(db.String(255))
    pass_left = db.Column(db.String(1))
    category = db.Column(db.String(255))
    text = db.Column(db.String(2048))
    insight = db.Column(db.String(2048))
    rating = db.Column(db.Integer)
    source = db.Column(db.String(255))
