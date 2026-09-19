class Movie:
    def __init__(self, title, status,rating= 0):
        self.title = title
        self.status = status
        self.rating = rating
    def show_details(self):
        print("Title:", self.title)
        print("Status:", self.status)

        if self.status == "watchlist":
            print("Rating: Not Watched Yet")
        else:
            print("Rating", self.rating)
        print()
    def review(self):
        if self.rating >= 8:
            print("Great movie")
        elif self.rating >= 5:
            print("Good movie")
        else:
            print("Average movie")
    def is_watchlist(self):
        return self.status == "watchlist"
    def mark_watched(self, rating):
        self.status = "watched"
        self.rating = rating

    def __str__(self):
        return f"Title: {self.title}\nStatus: {self.status}\nRating: {self.rating}\n"
    def is_watched(self):
        return self.status == "watched"
def add_movie():
    title = input("Enter movie name: ")
    status = input("Watched or Watchlist: ").lower()
    if status == "watched":
        rating = int(input("Rating:"))
        movie = Movie(title, status,rating)
        movie.review()

    else:
        print("Added to Watchlist")
        movie = Movie(title, status)

    return movie
def load_movies():
    movies = []
    with open("movies.txt", "r") as f:
        lines = f.readlines()

    for i in range(0, len(lines), 3):
        title = lines[i].replace("Title: ", "").strip()
        status = lines[i+1].replace("Status: ", "").strip()
        rating = int(lines[i+2].replace("Rating: ", "").strip())
        movie = Movie(title, status, rating)
        movies.append(movie)
    return movies
def save_movies(movies):
    with open("movies.txt", "w") as f:
        for movie in movies:
            f.write(str(movie))

def find_movie(movie_name, movies):
    for movie in movies:
        if movie.title.lower() == movie_name.lower():
            return movie
        
    return None 
user = input("Enter your name:")
print("Hello", user)
movies = load_movies()
while True:
    print("1. Add Movies")
    print("2. Show Movies")
    print("3. Search Movie")
    print("4. Show Watched Movies")
    print("5. Exit")
    print("6. Show watchlist")
    print("7. Mark Watchlist Movie as Watched")
    print("8. Delete Movie")
    print("9. Edit Rating")
    print("10. Show Movies Statistics")
    print("11. Show Top Rated Movies")
    choice = int(input("Enter your choice: "))

    if choice == 5:
        print("Exit")
        break
    if choice == 1:
        for i in range(3):
            movie = add_movie()
            movies.append(movie)
        save_movies(movies)
        print("\nMovies Added:")
        for movie in movies:
            movie.show_details()
    elif choice == 2:
        for movie in movies:
            movie.show_details()
    elif choice == 3:
        print("Search Movie")
        search_movie = input("Enter movie name: ").lower()
        movie = find_movie(search_movie, movies)
        if movie:
            movie.show_details()
        else:
            print("Movie not found! ")
    elif choice == 4:
        print("Watched Movies:")

        for movie in movies:
            if movie.is_watched():
                movie.show_details()
    elif choice == 6:
        print("watchlist Movies:")

        for movie in movies:
            if movie.is_watchlist():
                movie.show_details() 
    elif choice == 7:
        movie_name = input("Enter the Name: ")
        movie = find_movie(movie_name, movies)
        if movie.is_watchlist():
                    rating = int(input("Enter rating: "))
                    movie.mark_watched(rating)
                    save_movies(movies)
                    print("Movie Updated!")
                    movie.show_details()
        else:
                    print("Movie already watched!")
        break
        if found == False:
            print("Movie not found! ")

    elif choice == 8:
        movie_name = input("Enter the Movie: ")
        found = False
        for movie in movies:
            if movie.title.lower() == movie_name.lower():
             found = True
             movies.remove(movie)
             save_movies(movies)
             print("Movie Deleted")
             break
        if found == False:
            print("Movie not found!")

    elif choice == 9:
        movie_name = input("Enter the movie name to change it's rating: ")
        found = False
        for movie in movies:
            if movie.title.lower() == movie_name.lower():
                found = True
                if movie.is_watched():
                    rating = int(input("Enter your new rating: "))
                    movie.rating = rating
                    save_movies(movies)
                    print("Rating Updated!")
                    movie.show_details()
                else:
                    print("Cannot edit rating of a watchlist movie!")
        if found == False:
            print("Movie Not Found!")
    
    elif choice == 10:
        total_movies = len(movies)

        watched_count = 0
        total_rating = 0
        for movie in movies:
            if movie.is_watched():
                watched_count += 1
                total_rating += movie.rating

        watchlist_count = total_movies - watched_count

        if watched_count > 0:
            average_rating = total_rating / watched_count
        else:
            average_rating = 0

        print("\n======= Movie Statistics========")
        print("Total Movies:", total_movies)
        print("Watched Movies:", watched_count)
        print("Watchlist Movies:", watchlist_count)
        print("Average Rating", round(average_rating, 2))

    elif choice == 11:
        watched_movies = []
        
        for movie in movies:
            if movie.is_watched(): watched_movies.append(movie)
        sorted_movies = sorted(
            watched_movies,
            key= lambda movie: movie.rating,
            reverse=True
        )
        print("\n===== Top Rated Movies =====")

        for movie in sorted_movies:
            movie.show_details()