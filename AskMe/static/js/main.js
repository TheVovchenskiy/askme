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
  const questionId = $(this).data("question-id");
  const answerId = $(this).data("answer-id");

  const voteId = questionId ? questionId : answerId;

  const bodyData = questionId
    ? "question_id=" + questionId
    : "answer_id=" + answerId;

  const request = new Request("http://127.0.0.1:8000/vote_up", {
    headers: {
      "X-CSRFToken": csrftoken,
      "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    },
    method: "POST",
    body: bodyData,
  });

  fetch(request).then((response_raw) =>
    response_raw.json().then((response_json) => {
      const voteCount = $(`#vote-count-${voteId}`);
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
  const questionId = $(this).data("question-id");
  const answerId = $(this).data("answer-id");

  const voteId = questionId ? questionId : answerId;

  const bodyData = questionId
    ? "question_id=" + questionId
    : "answer_id=" + answerId;

  const request = new Request("http://127.0.0.1:8000/vote_down", {
    headers: {
      "X-CSRFToken": csrftoken,
      "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    },
    method: "POST",
    body: bodyData,
  });

  fetch(request).then((response_raw) =>
    response_raw.json().then((response_json) => {
      const voteCount = $(`#vote-count-${voteId}`);
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

$(".correct-answer").on("click", function (ev) {
  const answerId = $(this).data("answer-id");
  const questionId = $(this).data("question-id");
  console.log(answerId);
  const bodyData = `answer_id=${answerId}&question_id=${questionId}`;
  console.log(bodyData);

  const request = new Request("http://127.0.0.1:8000/accept_answer", {
    headers: {
      "X-CSRFToken": csrftoken,
      "Content-type": "application/x-www-form-urlencoded;charset=UTF-8",
    },
    method: "POST",
    body: bodyData,
  });

  fetch(request)
    .then((response_raw) => response_raw.json())
    .then((response_json) => {
      console.log(response_json.correct_flag);
    })
    .catch((error) => {
      // Обработка ошибок, если необходимо
    });
});
