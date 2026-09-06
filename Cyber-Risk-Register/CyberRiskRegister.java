import java.util.ArrayList;
import java.util.List;
import java.util.Scanner;

public class CyberRiskRegister {
    private static final List<Risk> risks = new ArrayList<>();
    private static final Scanner scanner = new Scanner(System.in);

    public static void main(String[] args) {
        addSampleRisks();

        while (true) {
            printMenu();
            int choice = readNumber("Choose an option: ", 1, 4);

            if (choice == 1) {
                addRisk();
            } else if (choice == 2) {
                showRisks();
            } else if (choice == 3) {
                showSummary();
            } else {
                System.out.println("Risk register closed.");
                break;
            }
        }
    }

    private static void printMenu() {
        System.out.println("\n=== Cyber Risk Register ===");
        System.out.println("1. Add a risk");
        System.out.println("2. View all risks");
        System.out.println("3. View risk summary");
        System.out.println("4. Exit");
    }

    private static void addRisk() {
        System.out.print("Risk title: ");
        String title = scanner.nextLine().trim();

        System.out.print("Affected asset: ");
        String asset = scanner.nextLine().trim();

        int likelihood = readNumber("Likelihood (1-5): ", 1, 5);
        int impact = readNumber("Impact (1-5): ", 1, 5);

        risks.add(new Risk(risks.size() + 1, title, asset, likelihood, impact));
        System.out.println("Risk added successfully.");
    }

    private static void showRisks() {
        if (risks.isEmpty()) {
            System.out.println("No risks have been added.");
            return;
        }

        System.out.printf("\n%-4s %-28s %-20s %-10s %-8s%n",
                "ID", "Risk", "Asset", "Score", "Level");
        System.out.println("--------------------------------------------------------------------------");

        for (Risk risk : risks) {
            System.out.printf("%-4d %-28s %-20s %-10d %-8s%n",
                    risk.id,
                    shorten(risk.title, 27),
                    shorten(risk.asset, 19),
                    risk.getScore(),
                    risk.getLevel());
        }
    }

    private static void showSummary() {
        int high = 0;
        int medium = 0;
        int low = 0;

        for (Risk risk : risks) {
            if (risk.getLevel().equals("High")) {
                high++;
            } else if (risk.getLevel().equals("Medium")) {
                medium++;
            } else {
                low++;
            }
        }

        System.out.println("\n=== Risk Summary ===");
        System.out.println("Total risks: " + risks.size());
        System.out.println("High: " + high);
        System.out.println("Medium: " + medium);
        System.out.println("Low: " + low);
    }

    private static int readNumber(String message, int minimum, int maximum) {
        while (true) {
            System.out.print(message);
            String input = scanner.nextLine().trim();

            try {
                int number = Integer.parseInt(input);
                if (number >= minimum && number <= maximum) {
                    return number;
                }
            } catch (NumberFormatException ignored) {
                // The message below handles invalid text and out-of-range numbers.
            }

            System.out.println("Enter a number from " + minimum + " to " + maximum + ".");
        }
    }

    private static String shorten(String text, int maximumLength) {
        if (text.length() <= maximumLength) {
            return text;
        }
        return text.substring(0, maximumLength - 3) + "...";
    }

    private static void addSampleRisks() {
        risks.add(new Risk(1, "Phishing email exposure", "Employee accounts", 4, 4));
        risks.add(new Risk(2, "Outdated software", "Office computers", 3, 3));
    }

    private static class Risk {
        private final int id;
        private final String title;
        private final String asset;
        private final int likelihood;
        private final int impact;

        private Risk(int id, String title, String asset, int likelihood, int impact) {
            this.id = id;
            this.title = title;
            this.asset = asset;
            this.likelihood = likelihood;
            this.impact = impact;
        }

        private int getScore() {
            return likelihood * impact;
        }

        private String getLevel() {
            int score = getScore();
            if (score >= 15) {
                return "High";
            }
            if (score >= 6) {
                return "Medium";
            }
            return "Low";
        }
    }
}
