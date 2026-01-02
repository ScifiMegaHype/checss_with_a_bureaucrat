const socket = io();

// -------------------- SETUP --------------------
const room = prompt("Enter room name:");
socket.emit("join", { room });

const canvas = document.getElementById("board");
canvas.width = 480;
canvas.height = 480 + 30; // Extra space for status text
const ctx = canvas.getContext("2d");

const SIZE = 60;

let board = [];
let turn = "white";
let inCheck = false;

let selected = null;
let legalMoves = [];

// -------------------- SOCKET LISTENERS --------------------

socket.on("state", data => {
  board = data.board;
  turn = data.turn;
  inCheck = data.check;

  selected = null;
  legalMoves = [];

  draw();
});

socket.on("legal_moves", data => {
  selected = data.from;
  legalMoves = data.moves;
  draw();
});

// -------------------- INPUT --------------------

canvas.addEventListener("click", e => {
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  const col = Math.floor(x / SIZE);
  const row = Math.floor(y / SIZE);

  if (!selected) {
    // Ask server for legal moves
    socket.emit("select", {
      room: room,
      pos: [row, col]
    });
  } else {
    // Attempt move
    socket.emit("move", {
      room: room,
      move: [selected[0], selected[1], row, col]
    });

    selected = null;
    legalMoves = [];
  }
});

// -------------------- DRAWING --------------------

function draw() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  for (let r = 0; r < 8; r++) {
    for (let c = 0; c < 8; c++) {
      // Board square
      ctx.fillStyle = (r + c) % 2 === 0 ? "#71f465ff" : "#808080";
      ctx.fillRect(c * SIZE, r * SIZE, SIZE, SIZE);

      // Highlight selected square
      if (selected && selected[0] === r && selected[1] === c) {
        ctx.strokeStyle = "green";
        ctx.lineWidth = 3;
        ctx.strokeRect(c * SIZE, r * SIZE, SIZE, SIZE);
      }

      // Highlight legal moves
      for (const [mr, mc] of legalMoves) {
        if (mr === r && mc === c) {
          ctx.strokeStyle = "lime";
          ctx.lineWidth = 3;
          ctx.strokeRect(c * SIZE + 5, r * SIZE + 5, SIZE - 10, SIZE - 10);
        }
      }

      // Piece
      const piece = board[r][c];
      if (piece !== ".") {
        ctx.fillStyle = piece === piece.toUpperCase() ? "white" : "black";
        ctx.font = "32px Arial";
        ctx.textAlign = "center";
        ctx.textBaseline = "middle";
        ctx.fillText(piece.toUpperCase(), c * SIZE + SIZE / 2, r * SIZE + SIZE / 2);
      }
    }
  }

  // Status text
  ctx.fillStyle = "black";
  ctx.font = "18px Arial";
  ctx.textAlign = "left";
  ctx.fillText(`Turn: ${turn.toUpperCase()}`, 10, canvas.height - 10);

  if (inCheck) {
    ctx.fillStyle = "red";
    check_sign = "under CHECK!";
    ctx.fillText(check_sign, 120, canvas.height - 10);
  }
}
