# Nginx setup

Copy blog.conf to /etc/nginx/sites-available/blog and enable it:

    sudo cp nginx/blog.conf /etc/nginx/sites-available/blog
    sudo ln -s /etc/nginx/sites-available/blog /etc/nginx/sites-enabled/blog
    sudo nginx -t && sudo systemctl reload nginx
