function calculateArea(length, width) {
    if (length <= 0 || width <= 0) {
        throw new Error("Length and width must be positive");
    }
    return length * width;
}

function calculatePerimeter(length, width) {
    return 2 * (length + width);
}

const greet = (name) => {
    console.log(`Greeting: ${name}`);
    return `Hello, ${name}!`;
};