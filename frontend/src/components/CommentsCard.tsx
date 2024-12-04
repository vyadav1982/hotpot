import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/lib/utils';
import { useFrappeGetDocList } from 'frappe-react-sdk';
import { formatDistanceToNow, format } from 'date-fns';
import { getDateObject } from '@/utils/dateConversions/utils';

const commentsCardVariants = cva('w-full', {
  variants: {
    size: {
      default: 'max-w-md',
      small: 'max-w-sm',
      large: 'max-w-full',
    },
    variant: {
      default: 'bg-background',
      outlined: 'bg-background border border-border',
    },
  },
  defaultVariants: {
    size: 'default',
    variant: 'default',
  },
});

interface Comment {
  name?: string;
  reference_doctype: string;
  reference_name?: string;
  content?: string;
  comment_email?: string;
  comment_by?: string;
  comment_type: string;
  owner: string;
  creation: string;
}

interface CommentsCardProps extends VariantProps<typeof commentsCardVariants> {
  reference_doctype: string;
  reference_name: string;
  className?: string;
}

function formatCreationTime(creationTime: string) {
  const date = getDateObject(creationTime);
  const timeAgo = formatDistanceToNow(date.toDate(), { addSuffix: true });

  const formattedDate = format(date.toDate(), 'MMM d, yyyy h:mm a');
  return `${formattedDate} (${timeAgo})`;
}

export default function CommentsCard({
  reference_doctype,
  reference_name,
  size,
  variant,
  className,
}: CommentsCardProps) {
  const {
    data: parsedComments,
    error,
    isLoading,
  } = useFrappeGetDocList<Comment>(
    'Comment',
    {
      fields: ['*'],
      filters: [
        ['reference_doctype', '=', reference_doctype],
        ['reference_name', '=', reference_name],
        ['comment_type', '=', 'Comment'],
      ],
      orderBy: {
        field: 'creation',
        order: 'desc',
      },
    },
    undefined,
    {
      revalidateOnFocus: false,
    },
  );

  if (isLoading)
    return <div className="p-4 text-center">Loading comments...</div>;
  if (error)
    return (
      <div className="p-4 text-center text-red-500">
        Error loading comments: {error.message}
      </div>
    );
  if (!parsedComments || parsedComments.length === 0)
    return (
      <div className="p-4 text-center text-gray-500">No comments found.</div>
    );

  return (
    <Card className={cn(commentsCardVariants({ size, variant }), className)}>
      <CardHeader>
        <CardTitle>Comments</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {parsedComments.map((comment) => (
          <div key={comment.name} className="flex items-start space-x-4">
            <Avatar className="mt-1">
              <AvatarFallback className="bg-primary text-primary-foreground">
                {(comment.comment_email ?? ' ')[0].toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div className="flex-1 space-y-1">
              <div className="flex items-center justify-between">
                <p className="text-sm font-medium">{comment.comment_email}</p>
                <time
                  className="text-xs text-gray-500"
                  dateTime={comment.creation}
                  title={formatCreationTime(comment.creation)}
                >
                  {formatDistanceToNow(
                    getDateObject(comment.creation).toDate(),
                    {
                      addSuffix: true,
                    },
                  )}
                </time>
              </div>
              <div
                className="prose prose-sm max-w-none text-sm text-gray-700"
                dangerouslySetInnerHTML={{ __html: comment.content || '' }}
              />
            </div>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
