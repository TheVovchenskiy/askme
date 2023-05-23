function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
const csrftoken = getCookie("csrftoken");

$(".vote-up").on("click", function (ev) {
  const request = new Request("http://127.0.0.1:8000/vote_up", {
    headers: {
      "X-CSRFToken": csrftoken,
      "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    },
    method: "POST",
    body: "question_id=" + $(this).data("id"),
  });

  fetch(request).then((response_raw) =>
    response_raw.json().then((response_json) => {
      const voteCount = $(`#vote-count-${$(this).data("id")}`);
      const newRating = response_json.new_rating;

      if (newRating > 0) {
        voteCount.text("+" + newRating);
        voteCount.addClass("vote-count-positive");
        voteCount.removeClass("vote-count-negative");
      } else if (newRating < 0) {
        voteCount.text(newRating);
        voteCount.addClass("vote-count-negative");
        voteCount.removeClass("vote-count-positive");
      } else {
        voteCount.text(newRating);
        voteCount.removeClass("vote-count-positive");
        voteCount.removeClass("vote-count-negative");
      }
    })
  );
});

$(".vote-down").on("click", function (ev) {
  const request = new Request("http://127.0.0.1:8000/vote_down", {
    headers: {
      "X-CSRFToken": csrftoken,
      "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    },
    method: "POST",
    body: "question_id=" + $(this).data("id"),
  });

  fetch(request).then((response_raw) =>
    response_raw.json().then((response_json) => {
      const voteCount = $(`#vote-count-${$(this).data("id")}`);
      const newRating = response_json.new_rating;

      if (newRating > 0) {
        voteCount.text("+" + newRating);
        voteCount.addClass("vote-count-positive");
        voteCount.removeClass("vote-count-negative");
      } else if (newRating < 0) {
        voteCount.text(newRating);
        voteCount.addClass("vote-count-negative");
        voteCount.removeClass("vote-count-positive");
      } else {
        voteCount.text(newRating);
        voteCount.removeClass("vote-count-positive");
        voteCount.removeClass("vote-count-negative");
      }
    })
  );
});
