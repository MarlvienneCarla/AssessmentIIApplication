import tkinter as tk
from tkinter import ttk, messagebox
import requests
from PIL import Image, ImageTk
import json

class MovieApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Creative Movie Information App")
        self.movies = []

        with open("list.JSON", "r") as file:
            self.movies = json.load(file)
        self.create_widgets()

        self.api_key = "YOUR_API_KEY"  

        self.style = ttk.Style(self.root)
        self.style.theme_use("clam")
        self.style.configure("TLabel", font=("Helvetica", 12), foreground="white")
        self.style.configure("TButton", font=("Helvetica", 12), foreground="white", background="#20B2AA")
        self.style.configure("TCombobox", font=("Helvetica", 12), foreground="white", background="#20B2AA")
        self.style.configure("Text", font=("Helvetica", 12))

        self.create_frames()
        self.create_widgets()

    def create_frames(self):
        self.search_frame = ttk.Frame(self.root, padding="10")
        self.search_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.result_frame = ttk.Frame(self.root, padding="10")
        self.result_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

    def create_widgets(self):
        # Search by title
        self.search_by_title_label = ttk.Label(self.search_frame, text="Search by Title:")
        self.search_by_title_label.grid(row=0, column=0, padx=5, pady=5)

        self.title_entry = ttk.Entry(self.search_frame, width=30)
        self.title_entry.grid(row=0, column=1, padx=5, pady=5)

        self.title_search_button = ttk.Button(self.search_frame, text="Search", command=self.search_by_title)
        self.title_search_button.grid(row=0, column=2, padx=5, pady=5)

        # Search by genre
        self.search_by_genre_label = ttk.Label(self.search_frame, text="Search by Genre:")
        self.search_by_genre_label.grid(row=1, column=0, padx=5, pady=5)

        self.genre_combobox = ttk.Combobox(self.search_frame, values=["Action", "Comedy", "Drama", "Science Fiction"])
        self.genre_combobox.grid(row=1, column=1, padx=5, pady=5)

        self.genre_search_button = ttk.Button(self.search_frame, text="Search", command=self.search_by_genre)
        self.genre_search_button.grid(row=1, column=2, padx=5, pady=5)

        # Results listbox
        self.results_listbox = tk.Listbox(self.result_frame, width=50, height=10)
        self.results_listbox.grid(row=0, column=0, padx=5, pady=5, columnspan=3)

        self.results_listbox.bind("<Double-Button-1>", self.show_movie_details)

        # Movie poster
        self.poster_label = ttk.Label(self.result_frame, text="Movie Poster:")
        self.poster_label.grid(row=1, column=0, padx=5, pady=5)

        self.poster_canvas = tk.Canvas(self.result_frame, width=150, height=220, bg="white")
        self.poster_canvas.grid(row=2, column=0, padx=5, pady=5)

        # Movie details
        self.details_label = ttk.Label(self.result_frame, text="Movie Details:")
        self.details_label.grid(row=1, column=1, padx=5, pady=5)

        self.details_text = tk.Text(self.result_frame, width=50, height=10)
        self.details_text.grid(row=2, column=1, padx=5, pady=5)

    def search_by_title(self):
        query = self.title_entry.get()
        self.search_movies(query)

    def search_by_genre(self):
        genre = self.genre_combobox.get()
        self.search_movies(genre, search_by_genre=True)

    def search_movies(self, query, search_by_genre=False):
        base_url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": self.api_key, "query": query}
        if search_by_genre:
            params["with_genres"] = self.get_genre_id(query)

        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            self.display_results(data["results"])
        else:
            messagebox.showerror("Error", "Failed to fetch data from the API.")

    def get_genre_id(self, genre):
        genre_mapping = {"Action": 28, "Comedy": 35, "Drama": 18, "Science Fiction": 878}
        return genre_mapping.get(genre, 28)  # Default to Action if genre is not found

    def display_results(self, results):
        self.results_listbox.delete(0, tk.END)
        for movie in results:
            self.results_listbox.insert(tk.END, f"{movie['title']} ({movie['release_date'][:4]})")

    def show_movie_details(self, event):
        selected_index = self.results_listbox.curselection()
        if not selected_index:
            return

        movie_title = self.results_listbox.get(selected_index)
        movie_title = movie_title.split(" (")[0]  # Remove the release year

        base_url = "https://api.themoviedb.org/3/search/movie"
        params = {"api_key": self.api_key, "query": movie_title}
        response = requests.get(base_url, params=params)

        if response.status_code == 200:
            data = response.json()
            if data["results"]:
                selected_movie = data["results"][0]
                self.display_movie_details(selected_movie)
            else:
                messagebox.showwarning("Warning", "No details found for the selected movie.")
        else:
            messagebox.showerror("Error", "Failed to fetch details from the API.")

    def display_movie_details(self, movie):
        self.details_text.delete(1.0, tk.END)
        self.details_text.insert(tk.END, f"Title: {movie['title']}\n"
                                         f"Release Date: {movie['release_date']}\n"
                                         f"Overview: {movie['overview']}")

        # Display movie poster
        poster_path = movie.get('poster_path')
        if poster_path:
            poster_url = f"https://image.tmdb.org/t/p/w342{poster_path}"
            poster_image = Image.open(requests.get(poster_url, stream=True).raw)
            poster_image = poster_image.resize((150, 220), Image.ANTIALIAS)
            self.poster_image = ImageTk.PhotoImage(poster_image)
            self.poster_canvas.create_image(0, 0, anchor=tk.NW, image=self.poster_image)

if __name__ == "__main__":
    root = tk.Tk()
    app = MovieApp(root)
    root.mainloop()
