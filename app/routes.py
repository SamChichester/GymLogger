from flask import render_template, flash, redirect, url_for, request, abort, jsonify
from flask_login import current_user, login_user, logout_user, login_required
import sqlalchemy as sa
from urllib.parse import urlsplit
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, ExerciseForm, EditExerciseForm, AddProgressionForm, PreferencesForm, EditProgressionForm, SendFriendRequestForm, ManageFriendRequestsForm
from app.models import User, Exercise, friendship, FriendRequest, Progression
from datetime import datetime, timezone


@app.route('/')
@app.route('/index')
@login_required
def index():
    user_exercises = db.session.scalars(current_user.exercises.select()).all()
    friend_exercises = db.session.scalars(
        sa.select(Exercise).where(
            Exercise.user_id.in_(
                db.session.scalars(current_user.friends.select().with_only_columns(User.id)).all()
            )
        )
    ).all()

    all_exercises = user_exercises + friend_exercises

    all_progressions = []
    for exercise in all_exercises:
        for progression in exercise.progressions:
            all_progressions.append(progression)

    all_progressions.sort(key=lambda x: x.date, reverse=True)

    return render_template('index.html', title='Home Page', exercises=all_progressions[:10])


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(sa.select(User).where(User.username == form.username.data))
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password.', 'danger')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('You are now a registered user!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/profile/<int:user_id>', methods=['GET', 'POST'])
@login_required
def profile(user_id):
    if user_id == current_user.id:
        form = ExerciseForm()
        if form.validate_on_submit():
            new_exercise = Exercise(
                exercise_name=form.exercise_name.data,
                user_id=current_user.id,
                author=current_user
            )
            db.session.add(new_exercise)
            db.session.commit()

            new_progression = Progression(rep=form.reps.data, weight=form.weight.data, date=datetime.now(timezone.utc), exercise_id=new_exercise.id)

            db.session.add(new_progression)
            db.session.commit()

            flash('Exercise and progression added successfully!', 'success')
            return redirect(url_for('profile', user_id=user_id))

        query = current_user.exercises.select()
        exercises = db.session.scalars(query).all()
        return render_template('profile.html', user=current_user, exercises=exercises, form=form)

    existing_friendship = db.session.scalar(
        sa.select(friendship)
            .where(friendship.c.user_id == current_user.id)
            .where(friendship.c.friend_id == user_id)
    )
    user = db.session.scalar(sa.select(User).where(User.id == user_id))
    if existing_friendship or user.is_public:
        exercises = db.session.scalars(user.exercises.select()).all()
        friends = db.session.scalars(user.friends.select()).all()
        sent_request = db.session.scalar(sa.select(FriendRequest).where(FriendRequest.sender_id == user.id and FriendRequest.receiver_id == current_user.id))

        return render_template('friend_profile.html', user=user, exercises=exercises, friends=friends, sent_request=sent_request)
    else:
        return render_template('not_friends.html')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/edit_exercise/<int:exercise_id>', methods=['GET', 'POST'])
@login_required
def edit_exercise(exercise_id):
    exercise = db.session.scalar(sa.select(Exercise).where(Exercise.id == exercise_id))
    if exercise is None:
        abort(404)
    if exercise.author != current_user:
        abort(403)

    edit_form = EditExerciseForm()
    add_form = AddProgressionForm()
    edit_progression_form = EditProgressionForm()

    edit_progression_form.progression_element.choices = [
        (progression.id, f'{progression.weight}{exercise.author.weight_unit} x {progression.rep} reps ({progression.simplified_date()})')
        for progression in exercise.progressions
    ]

    if edit_form.validate_on_submit() and edit_form.submit.data:
        exercise.exercise_name = edit_form.exercise_name.data
        db.session.commit()
        flash('Exercise updated successfully!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))

    if add_form.validate_on_submit() and add_form.submit.data:
        new_progression = Progression(rep=add_form.reps.data, weight=add_form.weight.data, date=datetime.now(timezone.utc), exercise_id=exercise.id)
        db.session.add(new_progression)
        db.session.commit()
        flash('Progression added successfully!', 'success')
        return redirect(url_for('profile', user_id=current_user.id))

    if edit_progression_form.validate_on_submit() and edit_progression_form.edit_submit.data:
        progression_id = edit_progression_form.progression_element.data
        progression = db.session.scalar(sa.select(Progression).where(Progression.id == progression_id))

        if progression:
            progression.rep = edit_progression_form.update_reps.data
            progression.weight = edit_progression_form.update_weight.data
            db.session.commit()
            flash('Progression updated successfully!', 'success')
        else:
            flash('Error updating progression.', 'danger')

        return redirect(url_for('profile', user_id=current_user.id))

    if edit_progression_form.validate_on_submit() and edit_progression_form.delete_submit.data:
        progression_id = edit_progression_form.progression_element.data
        progression = db.session.scalar(sa.select(Progression).where(Progression.id == progression_id))

        if progression:
            db.session.delete(progression)
            db.session.commit()
            flash('Progression deleted successfully!', 'success')
        else:
            flash('Error deleting progression.', 'danger')

        return redirect(url_for('profile', user_id=current_user.id))

    edit_form.exercise_name.data = exercise.exercise_name
    return render_template('edit_exercise.html', edit_form=edit_form, add_form=add_form, edit_progression_form=edit_progression_form, exercise=exercise)


@app.route('/delete_exercise/<int:exercise_id>', methods=['POST'])
@login_required
def delete_exercise(exercise_id):
    exercise = db.session.scalar(sa.select(Exercise).where(Exercise.id == exercise_id))
    if exercise is None:
        abort(404)
    if exercise.author != current_user:
        abort(403)

    db.session.delete(exercise)
    db.session.commit()
    flash('Exercise deleted successfully!', 'success')
    return redirect(url_for('profile', user_id=current_user.id))


@app.route('/preferences', methods=['GET', 'POST'])
@login_required
def preferences():
    form = PreferencesForm()
    if request.method == 'GET':
        form.weight_unit.data = current_user.weight_unit
        form.display_date.data = current_user.date_display
        form.privacy.data = 'true' if current_user.is_public else 'false'

    if form.validate_on_submit():
        if form.weight_unit.data:
            current_user.weight_unit = form.weight_unit.data
        if form.display_date.data:
            current_user.date_display = form.display_date.data
        if form.privacy.data:
            is_public = form.privacy.data == 'true'
            current_user.is_public = is_public
        db.session.commit()
        flash('Preferences Updated Successfully!', 'success')
        return redirect(url_for('preferences'))

    return render_template('preferences.html', title='Preferences', form=form)


@app.route('/get_progression_details')
@login_required
def get_progression_details():
    progression_id = request.args.get('id', type=int)
    if not progression_id:
        return jsonify({'error': 'No ID provided'}), 400

    progression = db.session.scalar(sa.select(Progression).where(Progression.id == progression_id))
    if not progression or progression.exercise.author != current_user:
        return jsonify({'error': 'Invalid ID or unauthorized access'}), 404

    return jsonify({
        'weight': progression.weight,
        'reps': progression.rep,
        'date': progression.date
    })


@app.route('/send_friend_request', methods=['GET', 'POST'])
@login_required
def send_friend_request():
    form = SendFriendRequestForm()
    if form.validate_on_submit():
        friend_code = form.friend_code.data
        friend = db.session.scalar(sa.select(User).where(User.friend_code == friend_code))

        if friend:
            if friend.id == current_user.id:
                flash('You cannot add yourself as a friend.', 'warning')
            else:
                existing_friendship = db.session.scalar(
                    sa.select(friendship)
                        .where(friendship.c.user_id == current_user.id)
                        .where(friendship.c.friend_id == friend.id)
                )
                if existing_friendship:
                    flash('You are already friends with this user.', 'warning')
                else:
                    existing_request = db.session.scalar(
                        sa.select(FriendRequest)
                            .where(FriendRequest.sender_id == current_user.id)
                            .where(FriendRequest.receiver_id == friend.id)
                    )

                    if existing_request:
                        flash('You have already send a friend request to this user.', 'warning')
                    else:
                        db.session.add(FriendRequest(sender_id=current_user.id, receiver_id=friend.id))
                        db.session.commit()
                        flash('Friend request sent successfully!', 'success')
        else:
            flash('No user found with that friend code.', 'danger')

        return redirect(url_for('friends'))
    return render_template('send_friend_request.html', form=form)


@app.route('/friends')
@login_required
def friends():
    query = current_user.friends.select()
    friends = db.session.scalars(query).all()

    sent_requests_query = db.session.execute(sa.select(FriendRequest).where(FriendRequest.sender_id == current_user.id)).scalars().all()
    received_requests_query = db.session.execute(sa.select(FriendRequest).where(FriendRequest.receiver_id == current_user.id)).scalars().all()

    return render_template('friends.html', friends=friends, sent_requests=sent_requests_query, received_requests=received_requests_query)


@app.route('/respond_friend_request/<int:request_id>', methods=['POST'])
@login_required
def respond_friend_request(request_id):
    friend_request = db.session.scalar(sa.select(FriendRequest).where(FriendRequest.id == request_id))

    if friend_request is None or friend_request.receiver_id != current_user.id:
        abort(403)

    action = request.form.get('action')
    if action == 'accept':
        db.session.execute(friendship.insert().values(user_id=current_user.id, friend_id=friend_request.sender.id))
        db.session.execute(friendship.insert().values(user_id=friend_request.sender.id, friend_id=current_user.id))
        db.session.delete(friend_request)
        db.session.commit()
        flash('Friend added successfully!', 'success')
    elif action == 'reject':
        db.session.delete(friend_request)
        db.session.commit()
        flash('Friend request rejected.', 'info')
    else:
        flash('Invalid action.', 'danger')

    return redirect(url_for('friends'))


@app.route('/unfriend/<int:friend_id>', methods=['POST'])
@login_required
def unfriend(friend_id):
    friend = db.session.scalar(sa.select(User).where(User.id == friend_id))
    query = current_user.friends.select()
    friends = db.session.scalars(query).all()

    if friend is None or friend not in friends:
        abort(404)

    # Remove the friend from the current user's friends
    current_user.friends.remove(friend)

    # Remove the current user from the friend's friends
    friend.friends.remove(current_user)

    # Commit the changes
    db.session.commit()

    flash('Friend removed successfully!', 'success')
    return redirect(url_for('friends'))
