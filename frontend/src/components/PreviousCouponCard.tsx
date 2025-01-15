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
  const [selectedEmoji, setSelectedEmoji] = useState('It was good');
  const [feedback, setFeedback] = useState('');
  const [feedbackPresent, setFeedbackPresent] = useState(false);
  const [isEditable, setIsEditable] = useState(true);
  useEffect(() => {
    if (coupon.emoji_reaction !== null && coupon.emoji_reaction !== '') {
      setSelectedEmoji(coupon.emoji_reaction);
      setFeedbackPresent(true);
      setIsEditable(false);
    }
    if (coupon.feedback !== null && coupon.feedback !== '') {
      setFeedback(coupon.feedback);
      setFeedbackPresent(true);
      setIsEditable(false);
    }
  }, [coupon]);
  const handleEmojiClick = (emoji: any) => {
    if (isEditable && emoji === selectedEmoji) {
      setSelectedEmoji('');
      return;
    }
    if (isEditable) {
      setSelectedEmoji(emoji);
    }
  };

  const handleFeedbackChange = (event: any) => {
    if (isEditable) {
      setFeedback(event.target.value);
    }
  };

  const handleSubmit = async () => {
    const res = await handleFeedbackSubmit({ coupon, selectedEmoji, feedback });
    if (res === 'submitted') {
      setIsEditable(false);
      setFeedbackPresent(true);
    }
  };

  return (
    <Card key={coupon.coupon_time + coupon.coupon_date + coupon.title} className={coupon.status==='Expired' ? `bg-gray-300` : ``}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between text-lg font-semibold">
          <div className=" flex-1 overflow-x-hidden text-left">
            {coupon.title}
          </div>
          {coupon.status && (
            <div
              className={`rounded-full px-3 py-1 text-sm font-normal text-black
            lg:mx-1 ${
              coupon.status === 'Consumed'
                ? 'bg-green-500 text-white'
                : coupon.status === 'Expired'
                  ? 'bg-red-500 text-white'
                  : 'bg-yellow-500 text-black'
            }`}
            >
              {coupon.status.toUpperCase()}
            </div>
          )}
        </CardTitle>
        <CardDescription className="text-center text-sm">
          {new Date(coupon.coupon_date).toLocaleDateString('en-GB', {
            day: '2-digit',
            month: 'short',
            year: 'numeric',
          })}
        </CardDescription>
      </CardHeader>
      <CardContent className="flex flex-col items-center space-y-4 p-6">
        <div className="flex w-full justify-around">
          <div title="Loved it!" onClick={() => handleEmojiClick('Loved it!')}>
            <SmilePlus
              className={`rounded-full ${!feedbackPresent && 'hover:bg-green-400'} ${selectedEmoji === 'Loved it!' && 'bg-green-400'}`}
            />
          </div>
          <div
            title="It was good"
            onClick={() => handleEmojiClick('It was good')}
          >
            <Smile
              className={`rounded-full ${!feedbackPresent && 'hover:bg-orange-400'} ${selectedEmoji === 'It was good' && 'bg-orange-400'}`}
            />
          </div>
          <div
            title="It was Okay"
            onClick={() => handleEmojiClick('It was Okay')}
          >
            <Meh
              className={`rounded-full ${!feedbackPresent && 'hover:bg-yellow-400'} ${selectedEmoji === 'It was Okay' && 'bg-yellow-400'}`}
            />
          </div>
          <div
            title="Didn't like it"
            onClick={() => handleEmojiClick("Didn't like it")}
          >
            <Frown
              className={`rounded-full ${!feedbackPresent && 'hover:bg-red-400'} ${selectedEmoji === "Didn't like it" && 'bg-red-400'}`}
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
            disabled={feedbackPresent || coupon.status === 'Expired'}
          />
          <Button
            className="w-1/4"
            onClick={handleSubmit}
            disabled={
              (feedback === '' && selectedEmoji === '') ||
              feedbackPresent ||
              coupon.status === 'Expired'
            }
          >
            Submit
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};
