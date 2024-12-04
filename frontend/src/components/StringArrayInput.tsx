import { KeyboardEvent } from 'react';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Plus, X } from 'lucide-react';

interface StringArrayInputProps {
  label: string;
  placeholder?: string;
  data: string[];
  onUpdate: (data: string[]) => void;
  readOnly?: boolean;
}

export function StringArrayInput({
  label,
  placeholder,
  data,
  onUpdate,
  readOnly = false,
}: StringArrayInputProps) {
  const addItem = (item: string) => {
    if (item.trim() && !readOnly) {
      const updatedItems = [...data, item.trim()];
      onUpdate(updatedItems);
    }
  };

  const removeItem = (index: number) => {
    if (!readOnly) {
      const updatedItems = data.filter((_, i) => i !== index);
      onUpdate(updatedItems);
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && e.currentTarget.value.trim() && !readOnly) {
      e.preventDefault();
      addItem(e.currentTarget.value);
      e.currentTarget.value = '';
    }
  };

  return (
    <div className="space-y-2">
      <Label htmlFor={label}>{label}</Label>
      {!readOnly && (
        <div className="flex space-x-2">
          <Input
            id={label}
            onKeyPress={handleKeyPress}
            placeholder={placeholder || `Add ${label.toLowerCase()}`}
          />
          <Button
            onClick={() => {
              const input = document.getElementById(label) as HTMLInputElement;
              addItem(input.value);
              input.value = '';
            }}
            size="icon"
            type="button"
            aria-label={`Add ${label}`}
          >
            <Plus className="h-4 w-4" />
          </Button>
        </div>
      )}
      <div className="flex flex-wrap gap-2">
        {data &&
          data.map((item, index) => (
            <Badge key={index} variant="secondary">
              {item}
              {!readOnly && (
                <Button
                  variant="ghost"
                  size="sm"
                  className="ml-2 h-4 w-4 p-0 hover:bg-destructive hover:text-destructive-foreground"
                  onClick={() => removeItem(index)}
                  aria-label={`Remove ${item}`}
                >
                  <X className="h-3 w-3" />
                </Button>
              )}
            </Badge>
          ))}
      </div>
    </div>
  );
}
