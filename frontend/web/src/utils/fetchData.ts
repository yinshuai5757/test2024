const fetchData = async <T>(url: string): Promise<T | null> => {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error("Network response was not ok");
    }
    return (await response.json()) as T;
  } catch (error) {
    console.error("Failed with your fetch operation:", error);
    return null;
  }
};

export default fetchData;
