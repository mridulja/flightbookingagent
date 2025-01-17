# CrewAIR Flight Booking Assistant

A conversational AI flight booking system powered by OpenAI's GPT-4, built with FastAPI and Gradio. This project simulates a flight booking assistant that can handle natural language queries, provide flight prices, and process bookings.

![image](https://github.com/user-attachments/assets/52b2eb57-7c3d-4b9b-ad39-6a0c885d9037)


## Features

- 🤖 Natural language processing for flight inquiries
- 💰 Real-time flight price checks
- ✈️ Simulated booking system
- 📧 Email confirmation handling
- 🔄 Stateful conversation management
- 🌙 Dark mode interface

## Prerequisites

- Python 3.11 or higher
- OpenAI API key
- Virtual environment (recommended)

## Installation

1. Clone the repository:
```

2. Create and activate a virtual environment:
```bash
# On Windows
python -m venv venv
.\venv\Scripts\activate

# On macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your OpenAI API key:
```env
OPENAI_API_KEY=your_api_key_here
```

## Usage

1. Start the application:
```bash
python day4.py
```

2. Open your browser and navigate to:
```
http://127.0.0.1:7871
```

3. Start chatting with the booking assistant!

Example conversation:
```
User: Hi, I'd like to book a flight to London
Assistant: A flight to London would be $799. Would you like to book this flight?
User: Yes, please
Assistant: Great! Could you please provide your full name?
...
```

## Project Structure

```
flightbookingagent/
├── flightBookingAgent.py    # Main application file
├── requirements.txt         # Project dependencies
├── .env.example            # Environment variables template
├── .env                    # Actual environment variables (not in git)
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

## Environment Variables

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key

## Dependencies

Main dependencies include:
- `openai`: OpenAI API client
- `gradio`: Web interface framework
- `python-dotenv`: Environment variable management
- `typing`: Type hints support

For a complete list, see `requirements.txt`.

## Development

To contribute to this project:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## Testing

Run the tests using:
```bash
python -m pytest
```

## Common Issues

1. **OpenAI API Error**: Make sure your API key is correctly set in `.env`
2. **Model Not Found**: Verify you're using a supported model name
3. **Port In Use**: Change the port if 7871 is already in use

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- OpenAI for providing the GPT-4 API
- Gradio team for the chat interface framework
- Contributors and maintainers

## Contact

Your Name - [your.email@example.com](mailto:your.email@example.com)

Project Link: [https://github.com/yourusername/flightbookingagent](https://github.com/yourusername/flightbookingagent)

## Version History

* 0.1
    * Initial Release
    * Basic booking functionality
    * Price checking implementation

## Contributing

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
