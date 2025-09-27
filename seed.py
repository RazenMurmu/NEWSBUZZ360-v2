from app import app, db
from models import Post
from werkzeug.security import generate_password_hash

# Dummy data for news posts
dummy_posts = [
    # --- Original 15 Posts ---
    {
        'title': "The Future of AI: What to Expect in the Next Decade",
        'subtitle': "Experts weigh in on the rapid advancements in artificial intelligence.",
        'content': "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus lacinia odio vitae vestibulum vestibulum.",
        'category': "technology",
        'featured': True  # Featured Post 1
    },
    {
        'title': "Local Sports Team Wins Championship in Thrilling Final",
        'subtitle': "A last-minute goal secures the victory after a hard-fought season.",
        'content': "Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas.",
        'category': "sports",
        'featured': True  # Featured Post 2
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
        'featured': True  # Featured Post 3
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
    },
    # --- 15 NEW Posts Added Below ---
    {
        'title': "Viral Recipe: The Ultimate Guide to Sourdough Bread",
        'subtitle': "Learn the secrets to baking the perfect loaf at home.",
        'content': "Sed posuere consectetur est at lobortis. Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus.",
        'category': "lifestyle",
        'featured': True  # Featured Post 4
    },
    {
        'title': "New Smartphone Released with Groundbreaking Camera",
        'subtitle': "A deep dive into the features of the most anticipated phone of the year.",
        'content': "Nulla vitae elit libero, a pharetra augue. Donec id elit non mi porta gravida at eget metus.",
        'category': "technology",
        'featured': False
    },
    {
        'title': "Hit TV Series Renewed for a Final Season",
        'subtitle': "Fans rejoice as the popular drama gets a conclusive ending.",
        'content': "Fusce dapibus, tellus ac cursus commodo, tortor mauris condimentum nibh, ut fermentum massa justo sit amet risus.",
        'category': "entertainment",
        'featured': False
    },
    {
        'title': "Global Markets React to Economic Forecast",
        'subtitle': "An analysis of the latest financial trends and what they mean for you.",
        'content': "Aenean lacinia bibendum nulla sed consectetur. Praesent commodo cursus magna, vel scelerisque nisl consectetur et.",
        'category': "news",
        'featured': False
    },
    {
        'title': "Underdog Team Makes an Unlikely Comeback",
        'subtitle': "A stunning performance in the semi-finals has everyone talking.",
        'content': "Vivamus sagittis lacus vel augue laoreet rutrum faucibus dolor auctor. Duis mollis, est non commodo luctus.",
        'category': "sports",
        'featured': False
    },
    {
        'title': "Exploring the Ethics of Gene Editing",
        'subtitle': "Scientists and ethicists debate the future of CRISPR technology.",
        'content': "Maecenas faucibus mollis interdum. Cras justo odio, dapibus ac facilisis in, egestas eget quam.",
        'category': "technology",
        'featured': False
    },
    {
        'title': "Annual Film Festival Announces Award Winners",
        'subtitle': "Independent film takes home the top prize in a surprise victory.",
        'content': "Donec sed odio dui. Cras justo odio, dapibus ac facilisis in, egestas eget quam.",
        'category': "entertainment",
        'featured': True  # Featured Post 5
    },
    {
        'title': "Urban Gardening: How to Grow Food in Small Spaces",
        'subtitle': "Tips for creating a thriving garden on your balcony or windowsill.",
        'content': "Nullam quis risus eget urna mollis ornare vel eu leo. Cum sociis natoque penatibus et magnis dis parturient montes.",
        'category': "lifestyle",
        'featured': False
    },
    {
        'title': "Record-Breaking Transfer rocks the Football World",
        'subtitle': "A historic deal is signed, setting a new benchmark for player transfers.",
        'content': "Integer posuere erat a ante venenatis dapibus posuere velit aliquet. Sed posuere consectetur est at lobortis.",
        'category': "sports",
        'featured': False
    },
    {
        'title': "International Space Station to Receive New Science Module",
        'subtitle': "The new addition will expand research capabilities in zero gravity.",
        'content': "Aenean eu leo quam. Pellentesque ornare sem lacinia quam venenatis vestibulum. Maecenas sed diam eget risus.",
        'category': "news",
        'featured': False
    },
    {
        'title': "The Future of Virtual Reality and the Metaverse",
        'subtitle': "Beyond gaming: How VR is set to change work, education, and social interaction.",
        'content': "Curabitur blandit tempus porttitor. Cras mattis consectetur purus sit amet fermentum.",
        'category': "technology",
        'featured': False
    },
    {
        'title': "Album Review: A New Sound from a Pop Icon",
        'subtitle': "A track-by-track breakdown of the most talked-about album of the year.",
        'content': "Vestibulum id ligula porta felis euismod semper. Morbi leo risus, porta ac consectetur ac, vestibulum at eros.",
        'category': "entertainment",
        'featured': False
    },
    {
        'title': "Minimalism as a Lifestyle: Declutter Your Life",
        'subtitle': "How living with less can lead to more happiness and freedom.",
        'content': "Donec ullamcorper nulla non metus auctor fringilla. Maecenas sed diam eget risus varius blandit sit amet non magna.",
        'category': "lifestyle",
        'featured': False
    },
    {
        'title': "Marathon Runner Smashes World Record",
        'subtitle': "A new chapter in athletic history is written in a stunning performance.",
        'content': "Nullam id dolor id nibh ultricies vehicula ut id elit. Donec sed odio dui.",
        'category': "sports",
        'featured': False
    },
    {
        'title': "Breakthrough in Alzheimer's Research Announced",
        'subtitle': "A new study offers hope for a potential treatment, marking a significant milestone.",
        'content': "Praesent commodo cursus magna, vel scelerisque nisl consectetur et. Vivamus sagittis lacus vel augue laoreet.",
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
        print("Database has been seeded successfully with 30 articles!")

if __name__ == '__main__':
    seed_data()