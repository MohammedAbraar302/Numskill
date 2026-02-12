from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, CandidateProfile, AssessmentScore, ChecklistResponse, GameScore
import json

assessment_bp = Blueprint('assessment', __name__, url_prefix='/api/assessment')

# Question banks
QUESTION_BANKS = {
    'magnitude': [
        {'q': 'Which is larger: 15 or 51?', 'options': ['15', '51'], 'a': '51'},
        {'q': 'Which is smaller: 102 or 98?', 'options': ['102', '98'], 'a': '98'},
        {'q': 'Which is largest: 33, 43, or 34?', 'options': ['33', '43', '34'], 'a': '43'},
        {'q': 'Which is smaller: 7 or 17?', 'options': ['7', '17'], 'a': '7'},
        {'q': 'Order from small to large: 9, 2, 5', 'options': ['9, 2, 5', '2, 5, 9'], 'a': '2, 5, 9'}
    ],
    'estimation': [
        {'q': '12 + 29 is approximately?', 'options': ['40', '50', '30'], 'a': '40'},
        {'q': '105 - 48 is approximately?', 'options': ['50', '100', '60'], 'a': '50'},
        {'q': 'Around how many apples in 4 bags of 6?', 'options': ['20', '40'], 'a': '20'},
        {'q': 'Estimate 72 / 9', 'options': ['8', '10'], 'a': '8'},
        {'q': 'Is 39 + 18 closer to 50 or 60?', 'options': ['50', '60'], 'a': '60'}
    ],
    'facts': [
        {'q': '7 + 6 = ?', 'options': ['13', '14', '12'], 'a': '13'},
        {'q': '8 × 5 = ?', 'options': ['40', '45', '35'], 'a': '40'},
        {'q': '9 - 2 = ?', 'options': ['6', '7', '8'], 'a': '7'},
        {'q': '18 / 3 = ?', 'options': ['6', '5', '7'], 'a': '6'},
        {'q': '4 + 9 = ?', 'options': ['13', '14', '15'], 'a': '13'}
    ],
    'sequencing': [
        {'q': '2, 4, 6, ?', 'options': ['8', '9', '10'], 'a': '8'},
        {'q': '10, 20, 30, ?', 'options': ['40', '50', '35'], 'a': '40'},
        {'q': '5, 10, 15, ?', 'options': ['18', '20'], 'a': '20'},
        {'q': '9, 7, 5, ?', 'options': ['3', '4'], 'a': '3'},
        {'q': '1, 2, 4, 8, ?', 'options': ['16', '10'], 'a': '16'}
    ],
    'spatial': [
        {'q': 'Which shape has 3 sides?', 'options': ['Triangle', 'Square'], 'a': 'Triangle'},
        {'q': 'A cube is?', 'options': ['2D', '3D'], 'a': '3D'},
        {'q': 'Which shape has parallel sides?', 'options': ['Circle', 'Rectangle'], 'a': 'Rectangle'},
        {'q': 'How many corners does a square have?', 'options': ['4', '3'], 'a': '4'},
        {'q': 'Which way is left?', 'options': ['←', '→'], 'a': '←'}
    ],
    'memory': [
        {'q': 'Remember these numbers: 5, 9. What was the first?', 'options': ['5', '9'], 'a': '5'},
        {'q': 'In 842, what is the last digit?', 'options': ['2', '4'], 'a': '2'},
        {'q': 'Recall: 7, 3, 1. What is the middle number?', 'options': ['3', '7'], 'a': '3'},
        {'q': 'Which number comes before 11?', 'options': ['10', '12'], 'a': '10'},
        {'q': 'In the number 60, the digits are 6 and...?', 'options': ['0', '1'], 'a': '0'}
    ]
}

CHECKLIST_QUESTIONS = [
    'Count backwards easily?',
    'Recognize number sequences?',
    'Use fingers for simple addition/subtraction (age 8+)?',
    'Estimate quantities accurately?',
    'Tell analog time and manage time?',
    'Quickly recall multiplication facts?',
    'Align numbers correctly for column math?',
    'Show high math anxiety or avoidance?'
]

# --- CANDIDATE PROFILE ENDPOINTS ---
@assessment_bp.route('/profile', methods=['POST'])
@jwt_required()
def save_profile():
    """Save candidate profile"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Delete existing profile if exists
        CandidateProfile.query.filter_by(user_id=user_id).delete()
        
        profile = CandidateProfile(
            user_id=user_id,
            child_name=data.get('child_name'),
            child_age=data.get('child_age'),
            parent_name=data.get('parent_name')
        )
        
        db.session.add(profile)
        db.session.commit()
        
        return jsonify({'message': 'Profile saved', 'profile': profile.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get candidate profile"""
    try:
        user_id = get_jwt_identity()
        profile = CandidateProfile.query.filter_by(user_id=user_id).first()
        
        if not profile:
            return jsonify({'profile': None}), 200
        
        return jsonify({'profile': profile.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- ASSESSMENT ENDPOINTS ---
@assessment_bp.route('/questions/<module>', methods=['GET'])
@jwt_required()
def get_questions(module):
    """Get questions for a module"""
    try:
        if module not in QUESTION_BANKS:
            return jsonify({'error': 'Invalid module'}), 400
        
        questions = QUESTION_BANKS[module]
        return jsonify({'questions': questions}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/score', methods=['POST'])
@jwt_required()
def save_score():
    """Save assessment score"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        module = data.get('module')
        score = data.get('score')
        total = data.get('total')
        answers = data.get('answers', {})
        
        percentage = (score / total * 100) if total > 0 else 0
        
        score_record = AssessmentScore(
            user_id=user_id,
            module_name=module,
            score=score,
            total_questions=total,
            percentage=percentage
        )
        score_record.set_answers(answers)
        
        db.session.add(score_record)
        db.session.commit()
        
        return jsonify({'message': 'Score saved', 'score': score_record.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/scores', methods=['GET'])
@jwt_required()
def get_scores():
    """Get all assessment scores for user"""
    try:
        user_id = get_jwt_identity()
        scores = AssessmentScore.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'scores': [s.to_dict() for s in scores]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- CHECKLIST ENDPOINTS ---
@assessment_bp.route('/checklist/questions', methods=['GET'])
@jwt_required()
def get_checklist_questions():
    """Get checklist questions"""
    return jsonify({'questions': CHECKLIST_QUESTIONS}), 200


@assessment_bp.route('/checklist', methods=['POST'])
@jwt_required()
def save_checklist():
    """Save checklist responses"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        responses = data.get('responses', {})
        
        # Calculate score (number of positive responses)
        total_score = sum(1 for v in responses.values() if v == True)
        
        # Delete existing checklist
        ChecklistResponse.query.filter_by(user_id=user_id).delete()
        
        checklist = ChecklistResponse(
            user_id=user_id,
            total_score=total_score
        )
        checklist.set_responses(responses)
        
        db.session.add(checklist)
        db.session.commit()
        
        return jsonify({'message': 'Checklist saved', 'checklist': checklist.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/checklist', methods=['GET'])
@jwt_required()
def get_checklist():
    """Get user's checklist response"""
    try:
        user_id = get_jwt_identity()
        checklist = ChecklistResponse.query.filter_by(user_id=user_id).first()
        
        if not checklist:
            return jsonify({'checklist': None}), 200
        
        return jsonify({'checklist': checklist.to_dict()}), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- GAME SCORE ENDPOINTS ---
@assessment_bp.route('/game-score', methods=['POST'])
@jwt_required()
def save_game_score():
    """Save game score"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        game_score = GameScore(
            user_id=user_id,
            game_name=data.get('game_name'),
            score=data.get('score')
        )
        
        db.session.add(game_score)
        db.session.commit()
        
        return jsonify({'message': 'Game score saved', 'game_score': game_score.to_dict()}), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


@assessment_bp.route('/game-scores', methods=['GET'])
@jwt_required()
def get_game_scores():
    """Get all game scores for user"""
    try:
        user_id = get_jwt_identity()
        game_scores = GameScore.query.filter_by(user_id=user_id).all()
        
        return jsonify({
            'game_scores': [gs.to_dict() for gs in game_scores]
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --- REPORT ENDPOINT ---
@assessment_bp.route('/report', methods=['GET'])
@jwt_required()
def get_report():
    """Generate comprehensive report for user"""
    try:
        user_id = get_jwt_identity()
        
        profile = CandidateProfile.query.filter_by(user_id=user_id).first()
        scores = AssessmentScore.query.filter_by(user_id=user_id).all()
        game_scores = GameScore.query.filter_by(user_id=user_id).all()
        checklist = ChecklistResponse.query.filter_by(user_id=user_id).first()
        
        return jsonify({
            'profile': profile.to_dict() if profile else None,
            'assessment_scores': [s.to_dict() for s in scores],
            'game_scores': [gs.to_dict() for gs in game_scores],
            'checklist': checklist.to_dict() if checklist else None
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
