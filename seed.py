from app import app, db
from models import Post
from werkzeug.security import generate_password_hash

# Dummy data for news posts
dummy_posts = [
    {
        'title': "The Future of AI: What to Expect in the Next Decade",
        'subtitle': "Experts weigh in on the rapid advancements in artificial intelligence.",
        'content': "Lorem ipsum dolor sit amet, consectetur adipiscing elit. ... (add more placeholder text here)",
        'category': "technology",
        'featured': True
    },
    {
        'title': "Local Sports Team Wins Championship in Thrilling Final",
        'subtitle': "A last-minute goal secures the victory after a hard-fought season.",
        'content': "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. ...",
        'category': "sports",
        'featured': True
    },
    {
        'title': "Top 5 Travel Destinations for the Summer",
        'subtitle': "Discover breathtaking locations for your next vacation.",
        'content': "Donec eu libero sit amet quam egestas semper. Aenean ultricies mi vitae est. Mauris placerat eleifend leo.",
        'category': "lifestyle",
        'featured': False
    },
    {
        'title': "New Breakthrough in Renewable Energy Sources",
        'subtitle': "A recent study unveils a new method for harnessing solar power more efficiently.",
        'content': "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
        'category': "technology",
        'featured': False
    },
    {
        'title': "Entertainment Industry Sees a Shift in Streaming Wars",
        'subtitle': "Major players are changing their strategies to attract more subscribers.",
        'content': "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.",
        'category': "entertainment",
        'featured': False
    },
    # --- Add 10 more posts for pagination ---
    {
        'title': "Guide to Healthy Eating on a Budget",
        'subtitle': "Simple tips and tricks for a nutritious diet without breaking the bank.",
        'content': "Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum.",
        'category': "lifestyle",
        'featured': False
    },
    {
        'title': "The Rise of E-Sports: More Than Just a Game",
        'subtitle': "How competitive gaming became a global phenomenon.",
        'content': "Integer posuere erat a ante venenatis dapibus posuere velit aliquet.",
        'category': "sports",
        'featured': False
    },
    {
        'title': "Cybersecurity Threats to Watch Out For in 2025",
        'subtitle': "Protect your digital life from emerging online dangers.",
        'content': "Curabitur blandit tempus porttitor. Nullam quis risus eget urna mollis ornare vel eu leo.",
        'category': "technology",
        'featured': True
    },
    {
        'title': "Movie Premiere Shakes Up the Box Office",
        'subtitle': "The latest blockbuster is breaking records worldwide.",
        'content': "Vestibulum id ligula porta felis euismod semper.",
        'category': "entertainment",
        'featured': False
    },
    {
        'title': "City Announces New Public Transport Initiative",
        'subtitle': "A plan to improve urban mobility and reduce traffic congestion.",
        'content': "Maecenas sed diam eget risus varius blandit sit amet non magna.",
        'category': "news",
        'featured': False
    },
    {
        'title': "DIY Home Renovation Tips for Beginners",
        'subtitle': "Transform your living space with these easy-to-follow projects.",
        'content': "Cras mattis consectetur purus sit amet fermentum.",
        'category': "lifestyle",
        'featured': False
    },
    {
        'title': "Athlete Profile: The Journey to the Top",
        'subtitle': "An inside look at the life and training of a champion.",
        'content': "Donec ullamcorper nulla non metus auctor fringilla.",
        'category': "sports",
        'featured': False
    },
    {
        'title': "The Impact of 5G on Everyday Life",
        'subtitle': "How the next generation of wireless technology will change everything.",
        'content': "Praesent commodo cursus magna, vel scelerisque nisl consectetur et.",
        'category': "technology",
        'featured': False
    },
    {
        'title': "Upcoming Concerts and Music Festivals to Look Forward To",
        'subtitle': "A roundup of the most anticipated musical events of the year.",
        'content': "Nullam id dolor id nibh ultricies vehicula ut id elit.",
        'category': "entertainment",
        'featured': False
    },
    {
        'title': "Community Garden Project Brings Neighbors Together",
        'subtitle': "A local initiative is fostering community spirit and green spaces.",
        'content': "Morbi leo risus, porta ac consectetur ac, vestibulum at eros.",
        'category': "news",
        'featured': False
    }
]


def seed_data():
    with app.app_context():
        # Optional: Delete all existing posts to start fresh
        print("Deleting existing posts...")
        Post.query.delete()
        
        # Add new posts from the dummy data list
        print("Adding new posts...")
        for post_data in dummy_posts:
            post = Post(
                title=post_data['title'],
                subtitle=post_data['subtitle'],
                content=post_data['content'],
                category=post_data['category'],
                featured=post_data['featured']
            )
            db.session.add(post)
        
        # Commit the changes to the database
        db.session.commit()
        print("Database has been seeded successfully!")

if __name__ == '__main__':
    seed_data()