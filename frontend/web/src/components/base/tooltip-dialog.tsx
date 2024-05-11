import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog";
import { Separator } from "@radix-ui/react-select";
import { TooltipSvg } from "@/data/image/tooltip-svg";

type TooltipDialogProps = {
  title: string;
  children: React.ReactNode;
};

export const TooltipDialog = ({ title, children }: TooltipDialogProps) => {
  return (
    <Dialog>
      <DialogTrigger asChild>
        <button>
          <TooltipSvg />
        </button>
      </DialogTrigger>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <Separator />
        {children}
      </DialogContent>
    </Dialog>
  );
};
