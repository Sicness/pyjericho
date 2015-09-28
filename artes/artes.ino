#include <IRremote.h>
#include <Wire.h>
#include <Adafruit_MPL115A2.h>


#define PMSHole 2
#define PMSRoom 7
#define PMSKitchen 4
#define MOTIONTIMEOUT 15000

void setup();
void loop();
void IRCheck();
void MotionCheck();
void OnMotionChenged();
IRrecv irrecv(8);
IRsend irsend;
Adafruit_MPL115A2 mpl115a2;
long mpl115a2_lastTime = 0;
decode_results results;


class MotionSens
{
  private:
    long _lastTime; 
    byte _state;
    byte _pin;
    char* _name;
  public:
    MotionSens(char* name, uint8_t pin);
    void check();
};

MotionSens motionRoom("room", PMSRoom);
MotionSens motionHole("hole", PMSHole);
MotionSens motionKitchen("kitchen", PMSKitchen);

void OnMotionChenged();
void IRCheck();

void setup()
{
  Serial.begin(9600);
  Serial.setTimeout(50);  // ms
  irrecv.enableIRIn();
  mpl115a2.begin();
}

void loop()
{
  IRCheck();
  motionHole.check();
  motionRoom.check();
  motionKitchen.check();
  mpl115a2Check();
  serailRead();
}

void serailRead()
{
  String str;
  if (Serial.available() > 0)  {
    str = Serial.readString();
    if ((str.charAt(0) == 'I') && (str.charAt(1) == 'R')) {  // IR
      if (str.charAt(4) == 'F')  {  Serial.println("OFF"); irsend.sendNEC(0xF740BF, 32); } //OFF
      if (str.charAt(4) == 'N')  { irsend.sendNEC(0xF7C03F, 32); Serial.println("ON"); }  //ON
    }
  }
}

void IRCheck()
{
  if (irrecv.decode(&results))
  {
      
    Serial.println(results.value, HEX);
    dump(&results);
    irrecv.resume(); // Receive the next value 
  }
}

void dump(decode_results *results) {
  int count = results->rawlen;
  if (results->decode_type == UNKNOWN) {
    Serial.println("Could not decode message");
  } 
  else {
    if (results->decode_type == NEC) {
      Serial.print("Decoded NEC: ");
    } 
    else if (results->decode_type == SONY) {
      Serial.print("Decoded SONY: ");
    } 
    else if (results->decode_type == RC5) {
      Serial.print("Decoded RC5: ");
    } 
    else if (results->decode_type == RC6) {
      Serial.print("Decoded RC6: ");
    }
    Serial.print(results->value, HEX);
    Serial.print(" (");
    Serial.print(results->bits, DEC);
    Serial.println(" bits)");
  }
  Serial.print("Raw (");
  Serial.print(count, DEC);
  Serial.print("): ");

  for (int i = 0; i < count; i++) {
    if ((i % 2) == 1) {
      Serial.print(results->rawbuf[i]*USECPERTICK, DEC);
    } 
    else {
      Serial.print(-(int)results->rawbuf[i]*USECPERTICK, DEC);
    }
    Serial.print(" ");
  }
  Serial.println("");
}

MotionSens::MotionSens(char* name, uint8_t pin)
{
      pinMode(pin, INPUT);
      _pin = pin;
      _state = LOW;
      _lastTime = millis();    
      _name = name;  
}

void MotionSens::check()
{
  byte new_state = digitalRead(_pin);
  byte changed = false;
  
  if ((_state == HIGH) && (new_state == LOW) && (millis() - _lastTime > MOTIONTIMEOUT))
  {
      _state = new_state;
      changed = true;
  }
  
  if ((_state == LOW) && (new_state == HIGH))
  {
    _state = new_state;
    changed = true;
    _lastTime = millis();
  }

  if ((_state == HIGH) && (new_state == HIGH))
        _lastTime = millis();
  
  if (changed)
  {
    Serial.print("Motion in ");
    Serial.print(_name);
    if (_state == HIGH)
      Serial.println(" YES");
    else
      Serial.println(" NO");
  }
}

void mpl115a2Check()
{
  if (millis() - mpl115a2_lastTime < 10000)
    return;
  mpl115a2_lastTime = millis();
    
  float pressureKPA = mpl115a2.getPressure();  
  Serial.print("Pressure="); Serial.println(pressureKPA, 4); 

  float temperatureC = mpl115a2.getTemperature();  
  Serial.print("Temp="); Serial.println(temperatureC, 1); 
}


