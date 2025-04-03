import { useState } from "react";
import Quagga, { QuaggaJSConfigObject } from "@ericblade/quagga2";

export default function useISBN13Scan(onDetected: (isbn13: string) => void) {
  const [isStarted, setIsStarted] = useState<boolean>(false);
  const [error, setError] = useState<Error>();

  const startCapture = (elementId: string) => {
    if (isStarted) {
      console.warn("capture is already started.");
      return;
    }
    Quagga.onDetected(async (result) => {
      const isbn = result.codeResult.code;
      if (isbn && isbn.startsWith("978") && isbn.length === 13) {
        onDetected(isbn);
        await Quagga.stop();
        setIsStarted(false);
        return;
      }
    });
    const elm = document.getElementById(elementId);
    if (!elm) {
      setError(new Error(`no element found.ID:${elementId}`));
      return;
    }
    const cong: QuaggaJSConfigObject = {
      inputStream: {
        name: "Live",
        type: "LiveStream",
        target: elm,
        constraints: {
          facingMode: "environment", // using back camera / not face
        },
        singleChannel: false,
      },
      decoder: {
        readers: ["ean_reader"], // for isbn13
      },
      locate: true,
      numOfWorkers: navigator.hardwareConcurrency || 4,
    };

    Quagga.init(cong, (error) => {
      if (error) {
        console.error(`Error: ${error}`, error);
        setError(error);
        setIsStarted(false);
        return;
      }
      Quagga.start();
      setIsStarted(true);
    });
  };

  const stopCapture = async () => {
    if (!isStarted) {
      return;
    }
    await Quagga.stop();
    setIsStarted(false);
  };

  return { error, startCapture, stopCapture };
}
