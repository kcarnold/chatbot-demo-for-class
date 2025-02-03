import streamlit as st
from openai import OpenAI
import json

client = OpenAI(
    api_key=st.secrets["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

def initialize_state():
    if 'board' not in st.session_state:
        st.session_state.board = [" "] * 9
    if 'game_over' not in st.session_state:
        st.session_state.game_over = False
    if 'ai_thinking' not in st.session_state:
        st.session_state.ai_thinking = ""

def check_winner(board):
    winning_combinations = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # Rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # Columns
        [0, 4, 8], [2, 4, 6]  # Diagonals
    ]
    for combo in winning_combinations:
        if board[combo[0]] != " " and board[combo[0]] == board[combo[1]] == board[combo[2]]:
            return board[combo[0]]
    if " " not in board:
        return "Tie"
    return None

def get_ai_move(board):
    board_str = "|".join(board)
    messages = [
        {"role": "system", "content": """You are playing tic-tac-toe as O. The board is represented as a string with positions 0-8, separated by |.
First, analyze 2-3 possible moves and explain your thinking for each. Then, make your final choice.
Format your response as JSON with two fields:
- "thinking": string explaining your analysis
- "move": integer 0-8 representing your chosen move"""},
        {"role": "user", "content": f"Current board: {board_str}\nWhat's your move?"}
    ]
    
    try:
        response = client.chat.completions.create(
            model="gemini-1.5-flash",
            messages=messages,
            n=1
        )
        content = response.choices[0].message.content
        content = content.replace("```json", "").replace("```", "").strip()
        response_data = json.loads(content)
        move = int(response_data["move"])
        st.session_state.ai_thinking = response_data["thinking"]
        
        if 0 <= move <= 8 and board[move] == " ":
            return move
    except Exception as e:
        st.error(f"AI Error: {str(e)}")
    
    return board.index(" ")

def handle_cell_click(position):
    if st.session_state.board[position] == " " and not st.session_state.game_over:
        # Player move
        st.session_state.board[position] = "X"
        
        winner = check_winner(st.session_state.board)
        if winner:
            st.session_state.game_over = True
        else:
            # AI move
            ai_move = get_ai_move(st.session_state.board)
            st.session_state.board[ai_move] = "O"
            
            winner = check_winner(st.session_state.board)
            if winner:
                st.session_state.game_over = True

def handle_new_game():
    st.session_state.board = [" "] * 9
    st.session_state.game_over = False
    st.session_state.ai_thinking = ""

def main():
    st.title("Tic-Tac-Toe vs AI")
    initialize_state()
    
    cols = st.columns(3)
    for i in range(9):
        col = cols[i % 3]
        col.button(
            st.session_state.board[i], 
            key=f"cell_{i}", 
            on_click=handle_cell_click,
            args=(i,),
            disabled=st.session_state.game_over
        )
    
    if st.session_state.ai_thinking:
        with st.expander("AI's Analysis", expanded=True):
            st.write(st.session_state.ai_thinking)
    
    winner = check_winner(st.session_state.board)
    if winner == "X":
        st.success("You won! 🎉")
    elif winner == "O":
        st.error("AI won! 🤖")
    elif winner == "Tie":
        st.info("It's a tie! 🤝")
        
    st.button("New Game", on_click=handle_new_game)

if __name__ == "__main__":
    main()