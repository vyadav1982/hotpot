import { Button } from './ui/button';

interface CardPaginationProps {
  page: number;
  totalPages: number | undefined;
  onPageChange: (page: number) => void;
}

const CardPagination = ({
  page,
  totalPages,
  onPageChange,
}: CardPaginationProps) => {
  return (
    <div className="flex flex-col items-center  justify-center  py-4 ">
      <div className="flex items-center gap-4  py-4 ">
        <Button
          variant="outline"
          size="sm"
          onClick={() => {
            if (page - 1 < 1) {
              return;
            } else {
              onPageChange(page - 1);
            }
          }}
          disabled={page == 1}
        >
          Previous
        </Button>
        <Button
          variant="outline"
          size="sm"
          onClick={() => onPageChange(page + 1)}
          disabled={
            totalPages == 0 ||
            (!!totalPages && page === Math.ceil(totalPages / 10))
          }
        >
          Next
        </Button>
        <div>
          Page {page} - {totalPages && Math.ceil(totalPages / 10)}
        </div>
      </div>
    </div>
  );
};

export default CardPagination;
