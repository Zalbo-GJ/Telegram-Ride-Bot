from datetime import datetime
import random
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message,InlineKeyboardButton,  InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart, Command
from states import RegistrationStates, RideBookingStates, RatingStates
from utils import save_users_to_file, save_ongoing_rides_to_file, save_ratings_reviews_history_to_file
from models import users, ongoing_rides, user_ratings, user_reviews, ride_history





def register_handlers(router: Router, bot: Bot):
    # Command to start the registration process
    @router.message(CommandStart())
    async def cmd_start(message: Message,  state: FSMContext):
        user_id = str(message.from_user.id)
        print( ride_history)
        if user_id in users:
            await state.set_state(RegistrationStates.PROFILE_EDIT)
            await message.reply("You have already registered.")
        else:
            users[user_id] = {}
            save_users_to_file(users=users)

            await state.set_state(RegistrationStates.NAME)
            await message.reply("Welcome! Let's start the registration process. What's your full name?")

    # Registration process
    @router.message(RegistrationStates.NAME)
    async def process_name(message: Message, state: FSMContext):
        user_id = str(str(message.from_user.id))
        users[user_id]['name'] = message.text
        save_users_to_file(users=users)
        await state.update_data(name=message.text)
        await state.set_state(RegistrationStates.PHONE)
        await message.answer("Please share your contact",reply_markup=ReplyKeyboardMarkup(
                    keyboard=[
                        [
                            KeyboardButton(text="Share Contact", request_contact=True),
                        
                        ]
                    ],
                    resize_keyboard=True,
                    one_time_keyboard=True
                    
                ),)
    @router.message(RegistrationStates.PHONE)
    async def process_phone(message: Message, state: FSMContext):
        user_id = str(message.from_user.id)
        users[user_id]['phone'] = message.contact.phone_number
        save_users_to_file(users=users)
        await state.update_data(phone=message.contact.phone_number)

        await state.set_state(RegistrationStates.ROLE)
        await message.reply("Got it! Are you a driver or a passenger?", reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="Driver"), KeyboardButton(text="Passenger")]],
            resize_keyboard=True,
            one_time_keyboard=True
        ))

    # Save user role
    @router.message(lambda message: message.text.lower() in ["driver", "passenger"], RegistrationStates.ROLE)
    async def process_role(message: Message, state: FSMContext):
        user_id = str(message.from_user.id)
        users[user_id]['role'] = message.text.lower()
        save_users_to_file(users=users)
        await state.update_data(role=message.text)
        
        data = await state.get_data()
        print(data)

        await state.set_state(RegistrationStates.PROFILE_EDIT)
        await message.reply("Registration complete! You can now edit your profile." ,reply_markup=ReplyKeyboardRemove())


    # Command to start the profile editing process
    @router.message(Command('edit_profile'))
    async def cmd_edit_profile(message: Message, state: FSMContext):
        user_id = str(message.from_user.id)
        if str(user_id) not in users:
            await message.reply("Please complete the registration process first with /start.")
            return

        await state.set_state(RegistrationStates.NAME)
        await message.reply("Please enter your new full name.")



    # Implement ride booking logic

    @router.message(Command('request_ride'))
    async def cmd_request_ride(message: Message, state: FSMContext):
        user_id = str(message.from_user.id)
        if str(user_id) not in users:
            await message.reply("Please complete the registration process first with /start.")
            return
        if users[user_id]['role'] == "driver":
            await message.reply("Only passengers can request rides.")
            return
        await state.set_state(RideBookingStates.REQUEST_START)
        await message.reply(f"Where would you like to start your ride?")
        
    @router.message(RideBookingStates.REQUEST_START)
    async def process_ride_start(message: Message, state: FSMContext):
        user_id = str(message.from_user.id)
        ongoing_rides[user_id] = {'start_location': message.text}
        save_ongoing_rides_to_file(ongoing_rides=ongoing_rides)

        await state.set_state(RideBookingStates.REQUEST_DESTINATION)
        await message.reply("Great! Now, please provide your destination.")

    @router.message(RideBookingStates.REQUEST_DESTINATION)
    async def process_ride_destination(message: Message, state: FSMContext):
        user_id = str(message.from_user.id)
        ongoing_rides[user_id]['destination'] = message.text
        save_ongoing_rides_to_file(ongoing_rides=ongoing_rides)

        await bot.send_message(user_id, "Searching for nearby drivers...")
        await state.set_state(RatingStates.RATING)
        for driver_user_id in users:
            if users[driver_user_id]['role'] == 'driver':
                await bot.send_message(driver_user_id, f"New ride request from user {user_id}. Start: {ongoing_rides[user_id]['start_location']}, Destination: {ongoing_rides[user_id]['destination']}.")
        
        ride_price = random.randint(10, 50)  

        ongoing_rides[user_id]['price'] = ride_price
        save_ongoing_rides_to_file(ongoing_rides=ongoing_rides)

        await message.reply(f"Your ride request has been sent to nearby drivers.Your estimated price is \b{ride_price} Birr. Please wait for a response. ")

    # Implement driver matching logic


    @router.message(Command('accept_ride'))
    async def cmd_accept_ride(message: Message, state: FSMContext):
        driver_id = str(message.from_user.id)
        if str(driver_id) not in users or users[str(driver_id)]['role'] != 'driver':
            await message.reply("Only registered drivers can accept rides.")
            return

        user_ids = [user_id for user_id in ongoing_rides if 'driver' not in ongoing_rides[user_id]]
        if not user_ids:
            await message.reply("No available ride requests at the moment.")
            return

        lst = []
        for user_id in user_ids:
            button = InlineKeyboardButton(text=f"Ride request from {user_id}" ,callback_data=user_id ) 
            print(button, "here are the buttons")
            lst.append(button)
        
        print(lst)

        await bot.send_message(driver_id, "Here are the available ride requests:", reply_markup=InlineKeyboardMarkup(inline_keyboard=[lst]))



    @router.callback_query(lambda c: True)
    async def process_callback(callback_query: CallbackQuery, state: FSMContext):
        driver_id = str(callback_query.from_user.id)
        user_id = str(callback_query.data) 

        ongoing_rides[user_id]['driver'] = driver_id 
        save_ongoing_rides_to_file(ongoing_rides=ongoing_rides)

        ride_info = ongoing_rides.copy() 
        ride_info[user_id]['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        ride_info[driver_id]['date'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        
          # Now you can process the ride request acceptance
        ri = ongoing_rides[user_id].copy()
        ri.pop('driver', None)
        if users[(driver_id)]['role'] == 'driver':
                ride_info[driver_id] = {'passenger' : user_id}
                ride_info[driver_id].update(ri)
                
         
        if users[(driver_id)]['role'] == 'passenger':
                ride_info[driver_id] = {'driver' : user_id}
        
        print(ride_info, "ride info", user_id, "user id", driver_id, "driver id")
        if user_id not in ride_history:
            ride_history[user_id] = []  
        ride_history[user_id].append(ride_info[user_id]) 
                     

        # Update ride history for driver
        if driver_id not in ride_history:
            ride_history[driver_id] = []  
        ride_history[driver_id].append(ride_info[driver_id])  
        
        print(ride_history, "ride history")

        save_ratings_reviews_history_to_file(ride_history=ride_history) 

        await bot.send_message(driver_id, f"You have accepted the ride request from user {user_id}. Start: {ongoing_rides[user_id]['start_location']}, Destination: {ongoing_rides[user_id]['destination']}.")
        await bot.send_message(user_id, f"Your ride request has been accepted by driver {driver_id}. Driver's details will be provided shortly.")

        await state.set_state(RatingStates.RATING)
        await bot.send_message(user_id, "How would you rate your ride? (1-5)")
        await bot.send_message(driver_id, "How would you rate your ride? (1-5)")

        await bot.answer_callback_query(callback_query.id)
                
    @router.message(RatingStates.RATING)
    async def process_rating(message: Message, state: FSMContext):
        user_id = str(message.from_user.id)
        try:
            rating = int(message.text)
            if 1 <= rating <= 5:
                user_ratings[user_id] = rating
                ride_history[user_id][-1]['rating'] = rating  

                save_ratings_reviews_history_to_file(ride_history=ride_history)
                await state.set_state(RatingStates.REVIEW)
                await message.reply("Thank you! Please provide a review for your ride.")
            else:
                await message.reply("Please enter a rating between 1 and 5.")
        except ValueError:
            await message.reply("Please enter a valid number between 1 and 5.")

    @router.message(RatingStates.REVIEW)
    async def process_review(message: Message, state: FSMContext):
        user_id = str(message.from_user.id)
        review = message.text
        user_reviews[user_id] = review
        ride_info = ride_history[user_id][-1]  
        ride_history[user_id][-1]['review'] = review  
        if 'driver' in ride_info:
            print("driver in ride info")
            driver_id = ride_info['driver']
            ride_history[driver_id][-1]['passenger_rating'] = user_ratings[user_id]
            ride_history[driver_id][-1]['passenger_review'] = review
        elif 'passenger' in ride_info:
            passenger_id = ride_info['passenger']
            ride_history[passenger_id][-1]['driver_rating'] = user_ratings[user_id]
            ride_history[passenger_id][-1]['driver_review'] = review

        save_ratings_reviews_history_to_file(ride_history=ride_history)
        await state.set_state(RegistrationStates.START)

        await message.reply("Thank you for your feedback!")
    # Handling History
    @router.message(Command('view_ride_history'))
    async def cmd_view_ride_history(message: Message):
        user_id = str(message.from_user.id)
        if str(user_id) not in users or (users[user_id]['role'] != 'driver' and users[user_id]['role'] != 'passenger'):
            await message.reply("Only registered drivers or passengers can use this command.")
            return
        print(ride_history, "ride history")
        if user_id not in ride_history:
            await message.reply("No ride history available.")
            return

        history_message = "Your ride history:\n"
        for ride_info in ride_history[user_id]:
            history_message += f"- {ride_info['start_location']} to {ride_info['destination']}\n"
            history_message += f"  Date: {ride_info['date']}\n"
            if 'rating' in ride_info:
                history_message += f"  Rating: {ride_info['rating']}\n"
                history_message += f"  Review: {ride_info['review']}\n"
                if 'driver_rating' in ride_info:
                    history_message += f"  Driver Rating: {ride_info['driver_rating']}\n"
                    history_message += f"  Driver Review: {ride_info['driver_review']}\n"
                if 'passenger_rating' in ride_info:
                    history_message += f"  Passenger Rating: {ride_info['passenger_rating']}\n"
                    history_message += f"  Passenger Review: {ride_info['passenger_review']}\n"
            history_message += "\n"

        await message.reply(history_message)

