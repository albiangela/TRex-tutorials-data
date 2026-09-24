# TRex tutorials

A static website with HTML, CSS and JavaScript. No build step or npm dependencies are required.

## Open in VS Code

1. Extract the ZIP.
2. In VS Code, choose **File → Open Folder** and select `trex-tutorial-local`.
3. Open `index.html` directly in your browser, or use a local server as described below.

## Run a local server

From the VS Code terminal, in this folder:

```sh
python3 -m http.server 8000
```

On Windows, if `python3` is unavailable:

```sh
py -m http.server 8000
```

Open http://localhost:8000 in your browser. Press Ctrl+C in the terminal to stop the server.

Alternatively, use the VS Code Live Server extension and choose **Open with Live Server** on `index.html`.

## Edit the website

- `index.html`: tutorial text, tabs, resource links and YouTube embed.
- `style.css`: black theme, layout and responsive styles.
- `script.js`: tab selection, keyboard navigation and URL fragments.
- `images/`: diagrams used in the overview.
- `quick-start.html`: original quick-start guide.

Save your changes and refresh the browser. The website can also be hosted on any static web host.

The tutorial and diagrams work offline. The embedded YouTube video and external resource links require internet access. This local copy is independent of the hosted site; editing it does not update the online version.
