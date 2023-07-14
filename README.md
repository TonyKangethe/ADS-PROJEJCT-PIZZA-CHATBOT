<h1 align="center">A Pizza Ordering Chatbot</h1>
<p align="center">Built using Rasa Open-Source Framework.</p>

### About the app:
A simple chatbot that is able to take pizza orders, show pizza menu, show pizza outlets, and show outlet working hours. 

This was an exploration on how conversational ML can be exploitated and implemented in e-commerce without the need for building complex apps or websites; with the possibility of processing orders. With Rasa, it provides flexible conversational AI framework for building such assistants for any domain.
This chatbot is not only capable of taking pizza orders, but also validate some of the responses with appropriate feedback.

### How it works:

A user selects one of the connected messaging channels i.e Slack, Facebook or Telegram

### Main libraries used:

| Libraries                                                                         | Purpose                                |
|***********************************************************************************|****************************************|
| [Rasa NLU](https://rasa.com/docs/rasa/nlu-training-data/)                         | Training your data                     |
| [Rasa SDK](https://rasa.com/docs/action-server/)                                  | Python SDK for running custom actions  |
| [Phonenumbers](https://pypi.org/project/phonenumbers/)                            | Validation of  phone numbers           |
| [TinyDB](https://pypi.org/project/pyowm/)                                         | A document oriented database           |
| [TensorFlow](https://rasa.com/docs/rasa/reference/rasa/utils/tensorflow/models/)  | To implement your model                |
| [datetime](https://docs.python.org/3/library/datetime.html)                       | Display dates and time                 |

### Main Features :pushpin:
<li>Process an order</li>
<li>Show menu</li>
<li>Show work hours</li>
<li>Show locations</li>


### Installation of RASA Open-Source :inbox_tray:

First, create and activate python virtual environment in your desired directory.
    Upgrade pip to the latest version.
        <code>pip3 install -U pip</code>
    Clone this repository.
        <code>git clone (GitHub repository Link)</code>
    Install dependecies. Open a new terminal, navigate to the directory of the cloned repository then run the following:
        <code>pip install -r requirements.txt</code>
    To talk to the chatbot, run the following on your terminal:
        <code>rasa shell</code>
    Additionally, open another new terminal, navigate to the same directory & run the code below; to activate our custom actions necessary to run the bot.
        <code>rasa run actions</code>


Incase of anything; ideas, suggestions or conributions feel free to reach out via [mail](tonnie9046@gmail.com) :e-mail:


### Author :black_nib:
#### Anthony Kangethe