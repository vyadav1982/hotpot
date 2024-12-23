import { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from './ui/card';
import { Frown, Meh, Smile, SmilePlus } from 'lucide-react';
import { Input } from './ui/input';
import { Button } from './ui/button';

export const PrevuousCouponCard = ({ coupon, handleFeedbackSubmit }: any) => {
  const [selectedEmoji, setSelectedEmoji] = useState('');
  const [feedback, setFeedback] = useState('');
  const [feedbackPresent, setFeedbackPresent]  =useState(false);
  const [isEditable,setIsEditable] = useState(true);
  useEffect(()=>{
    if(coupon.emoji_reaction!==null && coupon.emoji_reaction!==''){
      setSelectedEmoji(coupon.emoji_reaction);
      setFeedbackPresent(true);
      setIsEditable(false);
    }
    if(coupon.feedback!==null && coupon.feedback!==''){
      setFeedback(coupon.feedback);
      setFeedbackPresent(true);
      setIsEditable(false);
    }

  },[coupon])
  const handleEmojiClick = (emoji: any) => {
    if(isEditable && emoji===selectedEmoji){
      setSelectedEmoji('');
      return ;
    }
    if(isEditable){
      setSelectedEmoji(emoji);
    }
  };

  const handleFeedbackChange = (event: any) => {
    if(isEditable){
      setFeedback(event.target.value);
    }
  };

  const handleSubmit = () => {
    handleFeedbackSubmit({ coupon, selectedEmoji, feedback });
  };

  return (
    <Card key={coupon.coupon_time + coupon.coupon_date + coupon.title}>
      <CardHeader>
        <CardTitle className="text-center text-lg font-medium">
          {coupon.title}
        </CardTitle>
        <CardDescription className="text-center text-sm">
          {coupon.coupon_date}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center space-y-4 p-6">
        <div className="flex w-full justify-around">
          <div title="Loved it!" onClick={() => handleEmojiClick('Loved it!')}>
            <SmilePlus
              className={`rounded-full hover:bg-green-400 ${selectedEmoji === 'Loved it!' && 'bg-green-400'}`}
            />
          </div>
          <div
            title="It was good"
            onClick={() => handleEmojiClick('It was good')}
          >
            <Smile
              className={`rounded-full hover:bg-orange-400 ${selectedEmoji === 'It was good' && 'bg-orange-400'}`}
            />
          </div>
          <div
            title="It was Okay"
            onClick={() => handleEmojiClick('It was Okay')}
          >
            <Meh
              className={`rounded-full hover:bg-yellow-400 ${selectedEmoji === 'It was Okay' && 'bg-yellow-400'}`}
            />
          </div>
          <div
            title="Didn't like it"
            onClick={() => handleEmojiClick("Didn't like it")}
          >
            <Frown
              className={`rounded-full hover:bg-red-400 ${selectedEmoji === "Didn't like it" && 'bg-red-400'}`}
            />
          </div>
        </div>
        <div className="flex w-full items-center justify-center space-x-4">
          <Input
            type="text"
            placeholder="Feedback..."
            title="Type your feedback here"
            className="w-3/4"
            value={feedback}
            onChange={handleFeedbackChange}
          />
          <Button className="w-1/4" onClick={handleSubmit} disabled={feedback==='' && selectedEmoji==='' || feedbackPresent}>
            Submit
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};