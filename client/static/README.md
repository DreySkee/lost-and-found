# Lost & Found – Offline Search Guide

Hey there! 👋 This folder lets you explore all the found items **without** turning on the server or using the internet. Here’s how everything fits together.

## What’s in this folder?

- **search.html** – The main page. Open this in your browser to see the items.
- **search.css** – Makes the page look nice (colors, fonts, layout).
- **metadata.js** – Holds the list of items (their names, colors, pictures, etc.).
- **uploads/** – A folder full of the item pictures. The page shows these images.

## How do I use it?

1. Open the `uploads` folder and make sure you see all the pictures.
2. Double-click `search.html` (or right-click and choose “Open With → Your Browser”).
3. Wait a second and the page will load all the items.
4. Count how many there are or search by typing in the box.

> 💡 Tip: all the data is already inside the `metadata.js` file, so you don’t need the internet or any servers.

## How does it work?

1. The browser opens **search.html**.
2. That page pulls the list of items from **metadata.js**.
3. Each item has a picture stored in **uploads/**.
4. **search.css** makes everything look nice and tidy.

If something doesn’t show up, check these things:
- Did the pictures stay inside the `uploads` folder? (It’s picky!)
- Did you open `search.html` and not some other file?

Now you’re ready to run your own offline lost-and-found page. Have fun exploring! 🕵️‍♀️🪄
