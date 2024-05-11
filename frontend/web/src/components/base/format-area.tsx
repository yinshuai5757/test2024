import { useDisclosure } from "@/hooks/useDisclosure";
import { Fragment } from "react";
import { TooltipDialog } from "./tooltip-dialog";
import { TrashSvg } from "@/data/image/trash-svg";
import { ArrowLeftSvg } from "@/data/image/arrow-left-svg";

type FormatAreaProps = {
  title: string;
  userText: string;
  sampleText: string;
  generatedText?: string;
  onUserTextChange?: (text: string) => void;
};

const formatTextWithBreaks = (text: string) => {
  return text.split(/[\n\s]/).map((line: string, index: number) => (
    <Fragment key={index}>
      {line}
      <br />
    </Fragment>
  ));
};

const formatTextWithNewLine = (text: string): string => {
  const parts = text.split(/[\n\s]/);
  const result = parts.join("\n");

  return result;
};

export const FormatArea = (props: FormatAreaProps) => {
  const { isOpen, setIsOpen } = useDisclosure(false);
  const { title, userText, sampleText, onUserTextChange } = props;

  const handleUserTextChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    if (onUserTextChange) {
      onUserTextChange(e.target.value);
    }
  };

  return (
    <div className="flex flex-col bg-white">
      <div className="bg-inactive flex items-center justify-between pl-2">
        <h3 className="font-bold">{title}</h3>
        <div className="flex items-center space-x-2">
          <ArrowLeftSvg
            onClick={() => setIsOpen(!isOpen)}
            className={`cursor-pointer transition-transform duration-300 ${
              isOpen ? "scale-x-[-1]" : "scale-x-100"
            }`}
          />
          <TooltipDialog title={title}>
            <div>
              <ul className="list-disc space-y-4 pl-5">
                <li className="space-y-1">
                  <h3 className="font-bold">条項の選択</h3>
                  <div className="text-sm">
                    <p>
                      条項を選択すると生成される文章のサンプル「書面として生成される内容」と「AIへの指示内容」が表示されます。
                    </p>
                    <p>これらは編集することができます。</p>
                  </div>
                </li>
                <li className="space-y-1">
                  <h3 className="font-bold">条項の移動</h3>
                  <div className="text-sm">
                    <p>
                      条項をドラッグすることで条項の順番や階層を移動できます。
                    </p>
                  </div>
                </li>
                <li className="space-y-1">
                  <h3 className="font-bold">チェックボックス</h3>
                  <div className="text-sm">
                    <p>
                      チェックボックスで選択した条項の文章をAIで生成します。
                    </p>
                    <p>
                      またバケツアイコン
                      <span className="bg-inactive px-1">
                        <TrashSvg className="svg-gray inline-block size-3" />
                      </span>
                      をクリックすることで選択した条項を削除できます。
                    </p>
                  </div>
                </li>
              </ul>
            </div>
          </TooltipDialog>
        </div>
      </div>
      <div className={`min-h-output-textarea flex`}>
        <textarea
          className="min-h-output-textarea shadow-textarea w-full p-2 text-xs"
          onChange={handleUserTextChange}
          defaultValue={
            userText
              ? formatTextWithNewLine(userText)
              : formatTextWithNewLine(sampleText)
          }
        />
        <p
          className={`shadow-textarea bg-disabled overflow-hidden text-xs transition-all duration-300 ${
            isOpen
              ? "min-h-output-textarea w-full scale-x-100 p-2"
              : "size-0 scale-x-0"
          }`}
        >
          {formatTextWithBreaks(sampleText)}
        </p>
      </div>
    </div>
  );
};
