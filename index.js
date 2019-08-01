
let intervalID = window.setInterval(fetchRequest, 3000);

let tagCount = 0;
let s = new Set();
let stopped = false;
let ul = document.getElementById("tweets");
let status = document.getElementById("status");

function createLi(data) {
  let li = document.createElement("li");
  li.classList.add("list-group-item");
  li.innerHTML = (` <div class="col-2 twitter-text" style="z-index: 100; background-color: white;">
                      <img src=${data[0].user.profile_image_url_https}>
                    </div>
                    <div class="col-10 clickable" style="z-index: 500; background-color: white;">
                      <a href=${data[0].user.url}>${data[0].user.name}</a>
                      <p>${data[0].text}</p>
                    </div>`);

  let clickable = li.getElementsByClassName('clickable')[0];
  clickable.addEventListener('click', function (e) {
    cover.style.display = "none";

    if (input != "") {
      let commentBox = document.createElement("div");
      commentBox.className = 'commentBox';
      commentBox.textContent = input;
      commentBox.style['background-color'] = "lightgoldenrodyellow";
      commentBox.style['z-index'] = '999';
      commentBox.style['position'] = 'absolute';

      let rect = this.getBoundingClientRect();
      let x = (e.pageX - rect.left) + 10;
      let y = (e.pageY - rect.top);
      console.log(e.pageX, rect.left);
      commentBox.style.left = x + 'px';
      let deleteIcon = document.createElement("i");
      deleteIcon.className = "fas fa-times pl-2";
      deleteIcon.style.display = "inline";
      deleteIcon.style.opacity = "0.3";
      deleteIcon.style['z-index'] = '999';
      deleteIcon.id = "" + tagCount;

      commentBox.appendChild(deleteIcon);
      this.appendChild(commentBox);
      input = "";

      let h = commentBox.clientHeight;
      let w = commentBox.clientWidth;
      let tri = document.createElement('div');
      tri.id = "svg" + tagCount;
      tagCount += 1;

      tri.style['background-color'] = "transparent";
      tri.style['z-index'] = '990';
      tri.style['position'] = 'absolute';
      tri.style.display = '';
      tri.style.top = (y-h/2) + 'px';
      tri.style.left = (x-10) + 'px';
      commentBox.style.top = (y-h/2+2) + 'px';

      tri.innerHTML = `
        <svg width=${w+15} height=${h+2}>
          <polygon points="10,0 0,${h/2+1} 10,${h+2} ${w+15},${h+2} ${w+15},0" style="fill:lightgoldenrodyellow;stroke:black;stroke-width:1" />
        </svg>`;


      commentBox.before(tri);
      deleteIcon.addEventListener('click', function () {
        this.parentElement.remove();
        let deleteId = 'svg' + this.id;
        document.getElementById(deleteId).remove();
      })
    }
  });
  return li;
}

function fetchRequest() {
  if (!stopped && s.size < 5) {
    // specify a url, in this case our web server
    fetch('http://localhost:8082/feed/start')
    .then(res => res.json())
    .then(data => {
        if (!s.has(data[0].id)) {
          let li = createLi(data);
          ul.prepend(li);
          s.add(data[0].id);

          // update progress bar
          let bar = document.getElementById("bar");
          bar.style = "width: " + (20 * s.size) + "%;";
          bar.textContent = s.size + "/5";
        }
    })
    .catch(err => {
      //error catching
      console.log(err)
    });
  }
}

ul.addEventListener('click', function (e) {
  if (e.target.id === "btn") {
    if (e.target.style.backgroundColor === "yellow") {
      e.target.style.backgroundColor = "transparent";
    } else {
      e.target.style.backgroundColor = "yellow";
    }
  }
});

const followBtn = document.getElementById('follow');
followBtn.addEventListener('click', function (e) {
  if (followBtn.textContent == "Follow") {
    followBtn.textContent = "Following";
    followBtn.classList.remove("btn-outline-primary");
    followBtn.classList.add("btn-primary");
  } else {
    followBtn.textContent = "Follow";
    followBtn.classList.add("btn-outline-primary");
    followBtn.classList.remove("btn-primary");
  }
});

const stopBtn = document.getElementById('stop');
stopBtn.addEventListener('click', function (e) {
  stopped = true;
  status.textContent = "Stopped.";
});

const restartBtn = document.getElementById('restart');

restartBtn.addEventListener('click', function (e) {
  stopped = false;

  let bar = document.getElementById("bar");
  bar.style = "width: 0%;";
  bar.textContent = "0/5";

  status.textContent = "Showing pizza-related TwitterFeeds...";
  for (let tweet of ul.querySelectorAll("li")) {tweet.remove();}
  for (let comment of document.getElementsByClassName('commentBox')) {comment.remove();}
  s = new Set();
});




// Comment layer

const cover = document.getElementById('cover');

let switchBtn = document.getElementById('switch');
let commentInput = document.getElementById('commentInput');

switchBtn.addEventListener('click', function (e) {
  if (commentInput.style.display === "none") {
    commentInput.style.display = "";
    for (let comment of document.getElementsByClassName('commentBox')) {
      comment.style.display = '';
    }
    for (let box of document.getElementsByTagName('svg')) {
      box.style.display = '';
    }
    switchBtn.classList.remove("btn-outline-primary");
    switchBtn.classList.add("btn-primary");
    switchBtn.textContent = "Hide Tags";
  } else {
    commentInput.style.display = "none";
    for (let comment of document.getElementsByClassName('commentBox')) {
      comment.style.display = 'none';
    }
    for (let box of document.getElementsByTagName('svg')) {
      box.style.display = 'none';
    }
    switchBtn.classList.remove("btn-primary");
    switchBtn.classList.add("btn-outline-primary");
    switchBtn.textContent = "Show Tags";
  }
});

let publishBtn = document.getElementById("publish");
let input = "";

publishBtn.addEventListener('click', function (e) {
  cover.style.display = "";

  input = document.getElementById("input").value;
  document.getElementById("input").value = '';
});



// Popup when Chrome Dev Tools are opened

let div = document.createElement('div');
let loop = setInterval(() => {
  console.log(div);
  console.clear();
});

Object.defineProperty(div, "id", {get: () => { 
  clearInterval(loop);
  if (confirm("Checking my source code? Click OK to see my Linkedin Profile")) {
    window.open('https://www.linkedin.com/in/victorsongyw');
  }
}});



