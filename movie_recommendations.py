"""
Name: movie_recommendations.py
Date: March 23 2020
Author: Olivia Kallmeyer okallmeyer@sandiego.edu Stela Doncheva sdoncheva@sandiego.edu
Description: A program that implements a particular type of movie recommendation system
called collaborative filtering
"""

import math
import csv
from scipy.stats import pearsonr
class BadInputError(Exception):
    pass
class Movie_Recommendations:
    # Constructor
    def __init__(self, movie_filename, training_ratings_filename):
        """
        Initializes the Movie_Recommendations object from 
        the files containing movie names and training ratings.  
        The following instance variables should be initialized:
        self.movie_dict - A dictionary that maps a movie id to
               a movie objects (objects the class Movie)
        self.user_dict - A dictionary that maps user id's to a 
               a dictionary that maps a movie id to the rating
               that the user gave to the movie.    
        """
        
        self.movie_dict = self.create_movie_dict(movie_filename)
        self.user_dict = {}
        self.update_dicts(training_ratings_filename)


    def create_movie_dict(self, movie_filename): 
        movie_dict = {}
        f = open(movie_filename)
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"') # breaks each line into list of strings and keeps any commas withing the quotes
    
        next(csv_reader) # skips the first line
        for line in csv_reader: 
            movie_id = int(line[0])
            title = line[1]

            movie =  Movie(movie_id , title) # creates movie object and puts it into new variable called movie
            movie_dict[movie_id] = movie 
        f.close()
        return movie_dict 
  
            

    
    def update_dicts(self, training_ratings_filename): # makes the user dict
        user_dict = {}
        f = open(training_ratings_filename)
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"') # breaks each line into list of strings and keeps any commas withing the quotes
        next(csv_reader) # skips the first line

        for line in csv_reader: 
            user_id = int(line[0])
            movie_id = int(line[1]) 
            rating = float(line[2]) 
            if user_id in self.user_dict:
                #updates user dict
                rating_dict = self.user_dict[user_id]
                rating_dict[movie_id] = rating
                self.user_dict[user_id] = rating_dict 

            else:
                new_rating_dict = {}
                new_rating_dict[movie_id] = rating
                self.user_dict[user_id] = new_rating_dict

            #updates movie dict for the users who have seen the current movie
            movie = self.movie_dict[movie_id] 
            movie.users.append(user_id)
            self.movie_dict[movie_id] = movie
        f.close()


    def predict_rating(self, user_id, movie_id):
        """
        Returns the predicted rating that user_id will give to the
        movie whose id is movie_id. 
        If user_id has already rated movie_id, return
        that rating.
        If either user_id or movie_id is not in the database,
        then BadInputError is raised.
        """
        if movie_id in self.movie_dict and user_id in self.user_dict: # check if user_id and movie_id valid
            if movie_id in self.user_dict[user_id]:
                rating_dict = self.user_dict[user_id]
                return rating_dict[movie_id] # gets specific rating for movie id

            else:
                product_sum = 0
                similarity_sum = 0
                for rated_movie_id in self.user_dict[user_id]:
                    rated_movie = self.movie_dict[rated_movie_id]
                    similarity = rated_movie.get_similarity(movie_id, self.movie_dict, self.user_dict)
                    product =  self.user_dict[user_id][rated_movie_id] * similarity
                    product_sum += product
                    similarity_sum += similarity
                if similarity_sum == 0:
                    return 2.5
                product_sum/=similarity_sum
                return product_sum
        else:
            raise  BadInputError ("user_id or movie_id doesn't exist in the databse")

         
    def predict_ratings(self, test_ratings_filename):
        """
        Returns a list of tuples, one tuple for each rating in the
        test ratings file.
        The tuple should contain
        (user id, movie title, predicted rating, actual rating)
        """
        f = open(test_ratings_filename,"r")
        #f.readline()
        csv_reader = csv.reader(f, delimiter = ',', quotechar = '"') # breaks each line into list of strings and keeps any commas withing the quotes
        next(csv_reader)
        ratings = []
        for line in csv_reader:
            user_id = int(line[0])
            movie_id = int(line[1])
            actual_rating = float(line[2])
            predicted_rating = self.predict_rating(user_id, movie_id)
            ratings.append((user_id, self.movie_dict[movie_id].title, predicted_rating, actual_rating))     
        return ratings


        
    def correlation(self, predicted_ratings, actual_ratings):
        """
        Returns the correlation between the values in the list predicted_ratings
        and the list actual_ratings.  The lengths of predicted_ratings and
        actual_ratings must be the same.
        """
        return pearsonr(predicted_ratings, actual_ratings)[0]
        
class Movie: 
    """
    Represents a movie from the movie database.
    """
    def __init__(self, id, title):
        """ 
        Constructor.
        Initializes the following instances variables.  You
        must use exactly the same names for your instance 
        variables.  (For testing purposes.)
        id: the id of the movie
        title: the title of the movie
        users: list of the id's of the users who have
            rated this movie.  Initially, this is
            an empty list, but will be filled in
            as the training ratings file is read.
        similarities: a dictionary where the key is the
            id of another movie, and the value is the similarity
            between the "self" movie and the movie with that id.
            This dictionary is initially empty.  It is filled
            in "on demand", as the file containing test ratings
            is read, and ratings predictions are made.
        """
        self.id = int(id)
        self.title = title
        self.users = []
        self.similarities = {}


    def __str__(self):
        """
        Returns string representation of the movie object.
        Handy for debugging.
        """
        return  f"{self.id}, {self.title}"
        

    def __repr__(self):
        """
        Returns string representation of the movie object.
        """
        return  f"{self.id}, {self.title}, {self.users}, {self.similarities}"

    def get_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        If the similarity has already been computed, return it.
        If not, compute the similarity (using the compute_similarity
        method), and store it in both
        the "self" movie object, and the other_movie_id movie object.
        Then return that computed similarity.
        If other_movie_id is not valid, raise BadInputError exception.
        """

        if other_movie_id in movie_dict:
            if other_movie_id in self.similarities: 
                return self.similarities[other_movie_id] # gets the already computed similarity value 
            else:
                similarity = self.compute_similarity(other_movie_id, movie_dict, user_dict)
                self.similarities[other_movie_id] = similarity 
                other_movie = movie_dict[other_movie_id]
                other_movie.similarities[self.id] = similarity
                movie_dict[other_movie_id] = other_movie
                return similarity
        else:
            raise BadInputError("The movie Id is not valid")


    def compute_similarity(self, other_movie_id, movie_dict, user_dict):
        """ 
        Computes and returns the similarity between the movie that 
        called the method (self), and another movie whose
        id is other_movie_id.  (Uses movie_dict and user_dict)
        """
        # finds the avgerage diff
        avg_dif = 0
        count = 0 # it counts the people that have rated both movies
        for userid in user_dict:
            ratings_dict = user_dict[userid] # keeps track of all rating made by each user
            if self.id in ratings_dict and other_movie_id in ratings_dict: # check for both values
                rating1 = ratings_dict[self.id]
                rating2 = ratings_dict[other_movie_id]
                avg_dif += abs(rating1-rating2)
                count+=1

        if count == 0:
            return 0
        else:
            avg_dif/=count# finds avg diff
            similarity =  1 - (avg_dif/4.5)
            return similarity


if __name__ == "__main__":
    # Create movie recommendations object.
    movie_recs = Movie_Recommendations("movies.csv", "training_ratings.csv")

    # Predict ratings for user/movie combinations
    rating_predictions = movie_recs.predict_ratings("test_ratings.csv")
    print("Rating predictions: ")
    for prediction in rating_predictions:
        print(prediction)
    predicted = [rating[2] for rating in rating_predictions]
    actual = [rating[3] for rating in rating_predictions]
    correlation = movie_recs.correlation(predicted, actual)
    print(f"Correlation: {correlation}")    
