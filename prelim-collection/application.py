import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify, session
from app.forms import DemoForm
from app.utils import upload_demo_to_s3, upload_video_to_s3, generate_unique_folder_name
from app.models import UserResponse
import os
from werkzeug.exceptions import HTTPException, BadRequest, InternalServerError
from datetime import timedelta

# from config import Config
SECRET_KEY = os.urandom(32)

application = Flask(__name__)
application.config['SECRET_KEY'] = 'HHHHHHHHHHHHHHHHHHHHHHX'
application.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=24)



logging.info('Flask application has started.')
print("gi")


@application.errorhandler(404)
def not_found_error(error):
    logging.error(f'404 Error: {error}')
    return render_template('errors/404.html'), 404

@application.errorhandler(500)
def internal_error(error):
    logging.error(f'500 Error: {error}')
    return render_template('errors/500.html'), 500

@application.errorhandler(Exception)
def handle_exception(e):
    # Pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # Log the error
    logging.error(f'Unhandled Exception: {e}', exc_info=True)

    # Return a custom error page
    return render_template('errors/500.html'), 500

@application.before_request
def make_session_permanent():
    session.permanent = True

@application.route('/')
def index():
    logging.info('Rendering the intro page.')
    return render_template('intro.html')

@application.route('/consent')
def consent():
    logging.info('Rendering the consent page.')
    return render_template('consent.html')
 
@application.route('/demographics', methods=['GET', 'POST'])
def demographics():
    form = DemoForm()
    logging.info('Rendering the demographics page.')
    return render_template('demographics.html', form=form)


@application.route('/question1', methods=['GET', 'POST'])
def question1():
    if request.method == 'POST':
        logging.info('Received answer for question 1.')
        return redirect(url_for('question2'))
    
    logging.info('Rendering question 1 page.')
    return render_template('question1.html')


@application.route('/question2', methods=['GET', 'POST'])
def question2():
    if request.method == 'POST':
        logging.info('Received answer for question 2.')
        return redirect(url_for('question3'))
    
    logging.info('Rendering question 2 page.')
    return render_template('question2.html')


@application.route('/question3', methods=['GET', 'POST'])
def question3():
    if request.method == 'POST':
        logging.info('Received answer for question 3.')
        return redirect(url_for('question4'))
    
    logging.info('Rendering question 3 page.')
    return render_template('question3.html')


@application.route('/question4', methods=['GET', 'POST'])
def question4():
    if request.method == 'POST':
        responses = request.form.to_dict()
        audio_files = request.files.getlist('audio')
        user_response = UserResponse(responses, audio_files)
        logging.info('Received answer for question 4.')
        return redirect(url_for('debriefing'))
    
    logging.info('Rendering question 4 page.')
    return render_template('question4.html')


@application.route('/debriefing')
def debriefing():
    logging.info('Rendering the debriefing page.')
    return render_template('debriefing.html')


@application.route('/save-video', methods=['POST'])
def save_video():
    try:
        question_number = request.args.get('question')
        if not question_number:
            logging.warning('No question number provided.')
            raise BadRequest('No question number provided.')

        if 'video' not in request.files:
            logging.warning('No video file found in the upload request.')
            raise BadRequest('No video file uploaded.')

        video_file = request.files['video']
        if video_file.filename == '':
            logging.warning('No video selected in the upload request.')
            raise BadRequest('No selected file.')

        if video_file:
            # Get the participant's folder from the session
            folder_name = session.get('participant_folder')
            if not folder_name:
                logging.error('Participant folder not found in session.')
                raise InternalServerError('Participant folder not found.')

            # Upload the video to S3
            success = upload_video_to_s3(video_file, folder_name, question_number)
            if success:
                return jsonify({'success': 'File uploaded successfully'}), 200
            else:
                return jsonify({'error': 'Failed to upload video'}), 500
        else:
            raise BadRequest('File upload failed.')
    except Exception as e:
        logging.error(f'Error in save_video: {e}', exc_info=True)
        return jsonify({'error': str(e)}), 500

@application.route('/handle_demographics', methods=['POST'])
def handle_demographics():
    try:
        form = DemoForm()
        if form.validate_on_submit():
            # Process form data and store it in the session or database
            demographic_data = {
                "first_name": form.first_name.data,
                "last_name": form.last_name.data,
                "age": form.age.data,
                "email": form.email.data,
                "gender": form.gender.data,
                "type_of_participant": form.type_of_participant.data,
                "time_spent": form.time_spent.data,
                "platforms_used": form.platforms_used.data,
            }
            logging.info(f"Demographics submitted: {demographic_data}")
            folder_name = generate_unique_folder_name(
                demographic_data['first_name'], demographic_data['last_name']
            )
            session['participant_folder'] = folder_name

            logging.info(f"Generated folder name: {folder_name}")
            try:
                upload_demo_to_s3(demographic_data, folder_name)
            except Exception as e:
                logging.error(f"Error uploading demographics to S3: {e}", exc_info=True)
                return render_template('errors/500.html'), 500
            

            return redirect(url_for('question1'))
        else:
            logging.warning("Demographics form validation failed.")
            return render_template('demographics.html', form=form)
    except Exception as e:
        logging.error(f'Error in handle_demographics: {e}', exc_info=True)
        return render_template('errors/500.html'), 500




if __name__ == '__main__':
    application.run(debug=True, host='0.0.0.0', port=5000)
    #application.run(debug=True, host='0.0.0.0', port=5000, ssl_context=(cert.pem, key.pem))
